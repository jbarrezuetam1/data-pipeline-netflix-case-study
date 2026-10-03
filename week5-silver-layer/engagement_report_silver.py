"""
Silver layer transformation for the Netflix Engagement Report.

Takes the raw Bronze table and produces a clean Silver table:
- Title split into title_english and title_original (original-language
  title, when the source includes one after " // ")
- Release_Date: the literal text "NaN" converted to a real NULL, then
  cast from text to a DATE
- Runtime: the trailing asterisk stripped, then converted from
  "H:MM" text into a single decimal-hours number
- Available_Globally?: "Yes"/"No" converted to a real BOOLEAN, and the
  column renamed (Iceberg does not allow "?" in column names)
"""

from spark_session import get_spark_session

spark = get_spark_session()

# Step 1: load the Bronze table and make it queryable with spark.sql
bronze_df = spark.table("local.bronze.engagement_report")
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

# Step 4: write the result as a Silver Iceberg table.
spark.sql("CREATE NAMESPACE IF NOT EXISTS local.silver")

spark.sql("""
    CREATE OR REPLACE TABLE local.silver.engagement_report
    USING iceberg
    AS SELECT * FROM silver_engagement_report
""")

print("Written to Iceberg table: local.silver.engagement_report")

spark.sql("SELECT * FROM local.silver.engagement_report").show(20, truncate=False)

spark.stop()