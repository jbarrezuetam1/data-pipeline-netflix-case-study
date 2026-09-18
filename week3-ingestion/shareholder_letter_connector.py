import pdfplumber
import pandas as pd

file_path = "week3-ingestion/raw_files/FINAL-Q2-26-Shareholder-Letter.pdf"
quarters = ["Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]

with pdfplumber.open(file_path) as pdf:
    page = pdf.pages[6]  # page 7, 0-indexed
    tables = page.extract_tables()
    raw_blob = tables[0][1][0]  # the single messy cell with all regional data

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
    values = tokens[-5:]        # last 5 tokens are always the 5 quarterly values
    metric = " ".join(tokens[:-5])  # everything before that is the metric name

    for quarter, value in zip(quarters, values):
        records.append({
            "region": current_region,
            "metric": metric,
            "quarter": quarter,
            "value": value,
        })

df = pd.DataFrame(records)
print(df)
print(f"\nTotal rows: {len(df)}")

output_path = "week3-ingestion/output/shareholder_letter_bronze.parquet"
df.to_parquet(output_path, index=False)
print(f"Saved to {output_path}")