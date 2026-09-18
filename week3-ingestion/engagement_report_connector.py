import pandas as pd

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

# Save raw (bronze layer) as Parquet - no cleaning or transformation yet
output_path = "week3-ingestion/output/engagement_report_bronze.parquet"
combined.to_parquet(output_path, index=False)
print(f"\nSaved to {output_path}")