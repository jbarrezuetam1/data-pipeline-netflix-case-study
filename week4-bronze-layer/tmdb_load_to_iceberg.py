"""
Bronze layer ingestion (load step) for TMDB movie details.

Reads the raw JSON Lines file produced by tmdb_fetch_details.py and
writes it as an Iceberg table backed by MinIO. Spark infers the nested
schema (credits, keywords, genres, etc.) automatically; no flattening
happens here, since Bronze keeps data as close to its raw form as
possible (flattening belongs in Silver).
"""

from spark_session import get_spark_session

INPUT_PATH = "week4-bronze-layer/raw_files/tmdb_movie_details.jsonl"

spark = get_spark_session()

# Spark reads one JSON object per line and infers a schema, including
# nested structs (e.g. credits.cast) and arrays (e.g. keywords.keywords).
df = spark.read.json(INPUT_PATH)

print(f"Rows read: {df.count()}")
print("Schema:")
df.printSchema()

spark.sql("CREATE NAMESPACE IF NOT EXISTS local.bronze")

df.writeTo("local.bronze.tmdb_movies").createOrReplace()

print("Written to Iceberg table: local.bronze.tmdb_movies")

spark.stop()