"""
Silver layer transformation for the Shareholder Letter Regional
Breakdown table.

Takes the raw Bronze table (long format: one row per region/metric/
quarter, value stored as text) and produces a clean Silver table:
- metric values pivoted into their own columns (wide format)
- numeric columns cast from text (removing $, comma, and % symbols)
- quarter converted from text (e.g. "Q2'25") into a real date,
  using the last day of that quarter
"""

from spark_session import get_spark_session

spark = get_spark_session()

# Step 1: load the Bronze table and make it queryable with spark.sql
bronze_df = spark.table("local.bronze.shareholder_letter_regional_breakdown")
bronze_df.createOrReplaceTempView("bronze_shareholder_letter")

# Step 2: strip $, comma, and % from the raw text value, then cast to double.
# This works for both dollar amounts and percentages, since both are
# just text with symbols around a number.
spark.sql("""
    SELECT
        region,
        metric,
        quarter,
        CAST(REGEXP_REPLACE(value, '[$,%]', '') AS DOUBLE) AS value_numeric
    FROM bronze_shareholder_letter
""").createOrReplaceTempView("cleaned_values")

# Step 3: pivot metric values into their own columns.
spark.sql("""
    SELECT *
    FROM cleaned_values
    PIVOT (
        FIRST(value_numeric) FOR metric IN (
            'Revenue' AS revenue_millions,
            'Y/Y % Growth' AS yoy_growth_pct,
            'F/X Neutral Y/Y % Growth' AS fx_neutral_yoy_growth_pct
        )
    )
""").createOrReplaceTempView("pivoted")

# Step 4: convert quarter text (e.g. "Q2'25") into a real date,
# using the last day of that quarter.
# - regexp_extract pulls out the quarter number (1-4) and the 2-digit year
# - the quarter number * 3 gives the last month of that quarter
# - make_date builds a date from year/month/day, then last_day() rounds
#   it to the final day of that month
spark.sql("""
    SELECT
        region,
        quarter AS quarter_label,
        LAST_DAY(
            MAKE_DATE(
                2000 + CAST(REGEXP_EXTRACT(quarter, "'(\\\\d+)", 1) AS INT),
                CAST(REGEXP_EXTRACT(quarter, 'Q(\\\\d)', 1) AS INT) * 3,
                1
            )
        ) AS quarter_end_date,
        revenue_millions,
        yoy_growth_pct,
        fx_neutral_yoy_growth_pct
    FROM pivoted
""").createOrReplaceTempView("silver_shareholder_letter")

# Step 5: write the result as a Silver Iceberg table.
spark.sql("CREATE NAMESPACE IF NOT EXISTS local.silver")

spark.sql("""
    CREATE OR REPLACE TABLE local.silver.shareholder_letter_regional_breakdown
    USING iceberg
    AS SELECT * FROM silver_shareholder_letter
""")

print("Written to Iceberg table: local.silver.shareholder_letter_regional_breakdown")

spark.sql("SELECT * FROM local.silver.shareholder_letter_regional_breakdown ORDER BY region, quarter_end_date").show(60, truncate=False)

spark.stop()