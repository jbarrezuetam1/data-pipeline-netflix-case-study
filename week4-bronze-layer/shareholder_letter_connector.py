"""
Bronze layer ingestion for the Netflix Shareholder Letter (Regional
Breakdown table). Extracts the same raw table as the Week 3 connector,
then writes it as an Iceberg table backed by MinIO instead of a plain
Parquet file (see ADR-005, ADR-006).
"""

import pandas as pd
import pdfplumber
from spark_session import get_spark_session

FILE_PATH = "week3-ingestion/raw_files/FINAL-Q2-26-Shareholder-Letter.pdf"
QUARTERS = ["Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]


def parse_regional_breakdown(raw_blob: str, quarters: list[str]) -> list[dict]:
    """
    Parses the messy regional-breakdown cell extracted from the PDF into
    a list of {region, metric, quarter, value} records.

    The raw cell has one line per metric, grouped under region headers
    ending in ":". Each metric line ends with exactly 5 whitespace-
    separated values, one per quarter, in the same order as `quarters`.
    """
    lines = raw_blob.split("\n")

    records = []
    current_region = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.endswith(":"):
            current_region = line.rstrip(":")
            continue

        tokens = line.split()
        values = tokens[-5:]  # last 5 tokens are always the 5 quarterly values
        metric = " ".join(tokens[:-5])  # everything before that is the metric name

        for quarter, value in zip(quarters, values):
            records.append({
                "region": current_region,
                "metric": metric,
                "quarter": quarter,
                "value": value,
            })

    return records


def main():
    with pdfplumber.open(FILE_PATH) as pdf:
        page = pdf.pages[6]  # page 7, 0-indexed
        tables = page.extract_tables()
        raw_blob = tables[0][1][0]  # the single messy cell with all regional data

    records = parse_regional_breakdown(raw_blob, QUARTERS)

    df = pd.DataFrame(records)
    print(df)
    print(f"\nTotal rows: {len(df)}")

    # Convert the pandas DataFrame into a Spark DataFrame, then write it
    # as an Iceberg table inside the "bronze" MinIO bucket.
    spark = get_spark_session()
    spark_df = spark.createDataFrame(df)

    spark.sql("CREATE NAMESPACE IF NOT EXISTS local.bronze")

    spark_df.writeTo("local.bronze.shareholder_letter_regional_breakdown").createOrReplace()

    print("Written to Iceberg table: local.bronze.shareholder_letter_regional_breakdown")

    spark.stop()


if __name__ == "__main__":
    main()