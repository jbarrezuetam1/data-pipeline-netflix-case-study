import pdfplumber

file_path = "week3-ingestion/raw_files/FINAL-Q2-26-Shareholder-Letter.pdf"

with pdfplumber.open(file_path) as pdf:
    page = pdf.pages[6]  # page 7 is index 6 (0-based)
    tables = page.extract_tables()

    print(f"Number of tables found on page 7: {len(tables)}")

    for t_idx, table in enumerate(tables):
        print(f"\n=== Table {t_idx} ===")
        for row_idx, row in enumerate(table):
            print(f"Row {row_idx}: {row}")