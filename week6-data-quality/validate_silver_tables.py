"""
Data quality validation for the Silver layer tables, using
Great Expectations (ADR-008).

Rules validated per table are based only on facts we can verify —
either mathematical certainties (a count of views or hours can never
be negative), documented API limits (TMDB's vote_average is always
0-10), or categories already observed directly in the data (region,
content_type) — not assumptions about Netflix's actual business.
"""

import great_expectations as gx
from spark_session import get_spark_session

spark = get_spark_session()
context = gx.get_context()


def validate_table(spark_df, table_name, expectations):
    """Runs a list of Great Expectations expectations against a
    Spark DataFrame and prints a pass/fail report."""
    data_source = context.data_sources.add_spark(name=f"{table_name}_source")
    asset = data_source.add_dataframe_asset(name=f"{table_name}_asset")
    batch_definition = asset.add_batch_definition_whole_dataframe(f"{table_name}_batch")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": spark_df})

    suite = gx.ExpectationSuite(name=f"{table_name}_suite")
    suite = context.suites.add(suite)
    for expectation in expectations:
        suite.add_expectation(expectation)

    results = batch.validate(suite)

    print(f"\n=== {table_name} ===")
    print(f"Overall success: {results.success}")
    for result in results.results:
        status = "PASS" if result.success else "FAIL"
        print(f"  [{status}] {result.expectation_config.type} {result.expectation_config.kwargs}")

    return results


# --- Shareholder Letter ---
shareholder_df = spark.table("local.silver.shareholder_letter_regional_breakdown")
validate_table(
    shareholder_df,
    "shareholder_letter_regional_breakdown",
    [
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="revenue_millions", min_value=0
        ),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="region", value_set=["UCAN", "EMEA", "LATAM", "APAC"]
        ),
    ],
)

# --- Engagement Report ---
engagement_df = spark.table("local.silver.engagement_report")
validate_table(
    engagement_df,
    "engagement_report",
    [
        gx.expectations.ExpectColumnValuesToBeBetween(column="hours_viewed", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(column="views", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(column="runtime_hours", min_value=0),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="content_type", value_set=["series", "movie"]
        ),
    ],
)

# --- TMDB Movies ---
tmdb_df = spark.table("local.silver.tmdb_movies")
validate_table(
    tmdb_df,
    "tmdb_movies",
    [
        gx.expectations.ExpectColumnValuesToBeBetween(column="revenue", min_value=0),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="vote_average", min_value=0, max_value=10
        ),
    ],
)

spark.stop()