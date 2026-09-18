import pandas as pd

file_path = "week3-ingestion/raw_files/Engagement_Report_2024_Jul-Dec.xlsx"

# First, just list what sheets exist inside the file
excel_file = pd.ExcelFile(file_path)
print(f"Sheets found: {excel_file.sheet_names}")

# Peek at the first few rows of each sheet
for sheet in excel_file.sheet_names:
    print(f"\n=== Sheet: {sheet} ===")
    # header=4 tells pandas: real column names live on row index 4 (the 5th row)
    df = pd.read_excel(file_path, sheet_name=sheet, header=5, nrows=5)
    print(df)
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")