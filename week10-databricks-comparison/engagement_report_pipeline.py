# Databricks notebook source
print(spark.version)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.gold;
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.bronze.raw_files;

# COMMAND ----------

dbutils.fs.ls("/Volumes/workspace/bronze/raw_files/")

# COMMAND ----------

import pandas as pd

FILE_PATH = "/Volumes/workspace/bronze/raw_files/Engagement_Report_2024_Jul-Dec.xlsx"

SHEETS_CONFIG = {
    "TV": "series",
    "Film": "movie",
}


def sanitize_column_names(columns):
    """Same logic as the self-hosted connector, kept identical for a fair comparison."""
    sanitized = []
    for col in columns:
        col = col.replace(" ", "_")
        col = col.replace("(", "")
        col = col.replace(")", "")
        sanitized.append(col)
    return sanitized


all_records = []

for sheet_name, content_type in SHEETS_CONFIG.items():
    df = pd.read_excel(FILE_PATH, sheet_name=sheet_name, header=5)
    df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])
    df["content_type"] = content_type
    all_records.append(df)
    print(f"Sheet '{sheet_name}': {len(df)} rows loaded")

combined = pd.concat(all_records, ignore_index=True)
combined.columns = sanitize_column_names(list(combined.columns))
print(f"Total combined rows: {len(combined)}")

spark_df = spark.createDataFrame(combined)

(
    spark_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("workspace.bronze.engagement_report")
)

print("Written to Delta table: workspace.bronze.engagement_report")

# COMMAND ----------

# MAGIC    %pip install openpyxl

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

display(spark.table("workspace.bronze.engagement_report").limit(5))
print(spark.table("workspace.bronze.engagement_report").count())

# COMMAND ----------

# Step 1: load the Bronze table and make it queryable with spark.sql
bronze_df = spark.table("workspace.bronze.engagement_report")
bronze_df.createOrReplaceTempView("bronze_engagement_report")

# Step 2: split Title into title_english and title_original.
spark.sql("""
    SELECT
        *,
        TRIM(TRY_ELEMENT_AT(SPLIT(Title, '//'), 1)) AS title_english,
        COALESCE(
            TRIM(TRY_ELEMENT_AT(SPLIT(Title, '//'), 2)),
            TRIM(TRY_ELEMENT_AT(SPLIT(Title, '//'), 1))
        ) AS title_original
    FROM bronze_engagement_report
""").createOrReplaceTempView("split_titles")

display(spark.sql("SELECT Title, title_english, title_original FROM split_titles LIMIT 10"))

# COMMAND ----------

# Step 3: clean Release_Date, Runtime, and Available_Globally?.
spark.sql("""
    SELECT
        title_english,
        title_original,
        CASE
            WHEN Release_Date = 'NaN' THEN NULL
            ELSE CAST(Release_Date AS DATE)
        END AS release_date,
        Hours_Viewed AS hours_viewed,
        ROUND(
            TRY_CAST(REGEXP_EXTRACT(Runtime, '^(\\\\d+):', 1) AS DOUBLE)
                + TRY_CAST(REGEXP_EXTRACT(Runtime, ':(\\\\d+)', 1) AS DOUBLE) / 60.0,
            2
        ) AS runtime_hours,
        Views AS views,
        CASE
            WHEN `Available_Globally?` = 'Yes' THEN TRUE
            WHEN `Available_Globally?` = 'No' THEN FALSE
            ELSE NULL
        END AS available_globally,
        content_type
    FROM split_titles
""").createOrReplaceTempView("silver_engagement_report")

display(spark.sql("SELECT * FROM silver_engagement_report LIMIT 10"))
spark.sql("SELECT * FROM silver_engagement_report").printSchema()

# COMMAND ----------

# Step 4: write the result as a Silver Delta table.
spark.sql("""
    CREATE OR REPLACE TABLE workspace.silver.engagement_report
    AS SELECT * FROM silver_engagement_report
""")

print("Written to Delta table: workspace.silver.engagement_report")
print(spark.table("workspace.silver.engagement_report").count())

# COMMAND ----------

# Staging: same logic as stg_engagement_report.sql in the dbt project.
spark.sql("""
    select
        title_english,
        title_original,
        lower(trim(title_english)) as title_key,
        release_date,
        hours_viewed,
        views,
        runtime_hours,
        content_type
    from workspace.silver.engagement_report
""").createOrReplaceTempView("stg_engagement_report")

display(spark.sql("select * from stg_engagement_report limit 10"))

# COMMAND ----------

# Fact table: same logic as the dbt fact model for the Engagement Report.
spark.sql("""
    CREATE OR REPLACE TABLE workspace.gold.fact_engagement AS
    select
        er.title_english,
        cast(er.release_date as date) as release_date,
        er.hours_viewed,
        er.views,
        er.runtime_hours,
        er.content_type
    from stg_engagement_report er
""")

print(spark.table("workspace.gold.fact_engagement").count())
display(spark.table("workspace.gold.fact_engagement").limit(5))

# COMMAND ----------

# Title dimension: Engagement Report columns only (TMDB is out of scope for this slice).
spark.sql("""
    CREATE OR REPLACE TABLE workspace.gold.dim_title AS
    select
        er.title_english,
        er.title_original,
        er.content_type
    from stg_engagement_report er
""")

print(spark.table("workspace.gold.dim_title").count())
display(spark.table("workspace.gold.dim_title").limit(5))

# COMMAND ----------

# Date dimension: Engagement Report dates only (TMDB is out of scope for this slice).
spark.sql("""
    CREATE OR REPLACE TABLE workspace.gold.dim_date AS
    select distinct
        cast(release_date as date) as date_day,
        extract(year from cast(release_date as date)) as year,
        extract(quarter from cast(release_date as date)) as quarter,
        extract(month from cast(release_date as date)) as month
    from stg_engagement_report
    where release_date is not null
""")

print(spark.table("workspace.gold.dim_date").count())
display(spark.table("workspace.gold.dim_date").orderBy("date_day").limit(5))

# COMMAND ----------

for schema in ["bronze", "silver", "gold"]:
    print(f"--- workspace.{schema} ---")
    display(spark.sql(f"SHOW TABLES IN workspace.{schema}"))