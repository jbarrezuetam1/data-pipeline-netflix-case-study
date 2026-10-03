"""
Silver layer transformation for TMDB movie details.

Takes the raw Bronze table and produces a clean Silver table:
- budget and revenue: 0 (meaning "not reported") converted to NULL
- genres: array of {id, name} structs simplified to an array of
  genre names only; an empty array converted to NULL
- runtime renamed to runtime_minutes for clarity

All other columns (credits, keywords, production_companies, etc.)
are carried through unchanged, since this table has many nested
columns not yet needed for analysis.
"""

from pyspark.sql import functions as F
from spark_session import get_spark_session

spark = get_spark_session()

bronze_df = spark.table("local.bronze.tmdb_movies")

silver_df = (
    bronze_df
    # 0 means "not reported" for budget/revenue, not a real zero value.
    .withColumn(
        "budget",
        F.when(F.col("budget") == 0, None).otherwise(F.col("budget")),
    )
    .withColumn(
        "revenue",
        F.when(F.col("revenue") == 0, None).otherwise(F.col("revenue")),
    )
    # Extract just the genre names from the array of {id, name} structs.
    # transform() applies x.name to every element of the genres array,
    # similar to Python's map(). An empty resulting array becomes NULL.
    .withColumn(
        "genres",
        F.when(
            F.size(F.transform("genres", lambda x: x["name"])) == 0,
            None,
        ).otherwise(F.transform("genres", lambda x: x["name"])),
    )
    # Rename runtime to make its unit explicit.
    .withColumnRenamed("runtime", "runtime_minutes")
)

spark.sql("CREATE NAMESPACE IF NOT EXISTS local.silver")

silver_df.writeTo("local.silver.tmdb_movies").createOrReplace()

print("Written to Iceberg table: local.silver.tmdb_movies")

spark.sql("""
    SELECT title, release_date, runtime_minutes, budget, revenue,
           vote_average, genres, status
    FROM local.silver.tmdb_movies
""").show(10, truncate=False)

spark.stop()