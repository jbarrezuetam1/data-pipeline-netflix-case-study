"""
Bronze layer ingestion for the Netflix Engagement Report (TV + Film
sheets combined). Extracts the same raw data as the Week 3 connector,
then writes it as an Iceberg table backed by MinIO instead of a plain
Parquet file (see ADR-005, ADR-006).
"""

import pandas as pd
from spark_session import get_spark_session

file_path = "week3-ingestion/raw_files/Engagement_Report_2024_Jul-Dec.xlsx"

sheets_config = {
    "TV": "series",
    "Film": "movie",
}

all_records = []

for sheet_name, content_type in sheets_config.items():
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=5)

    # Drop the blank leading column that comes from the report's formatting
    df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")])

    # Tag each row with its content type before combining TV and Film together
    df["content_type"] = content_type

    all_records.append(df)
    print(f"Sheet '{sheet_name}': {len(df)} rows loaded")

# Combine both sheets into a single dataset
combined = pd.concat(all_records, ignore_index=True)
print(f"\nTotal combined rows: {len(combined)}")
print(f"Final columns: {list(combined.columns)}")

# Iceberg column names cannot contain spaces or parentheses, unlike
# pandas/Parquet column names. Replace them with underscores so the
# table can be created without errors.
combined.columns = (
    combined.columns
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)
print(f"Sanitized columns: {list(combined.columns)}")

# Convert the pandas DataFrame into a Spark DataFrame, then write it
# as an Iceberg table inside the "bronze" MinIO bucket.
spark = get_spark_session()
spark_df = spark.createDataFrame(combined)

spark.sql("CREATE NAMESPACE IF NOT EXISTS local.bronze")

spark_df.writeTo("local.bronze.engagement_report").createOrReplace()

print("Written to Iceberg table: local.bronze.engagement_report")

spark.stop()