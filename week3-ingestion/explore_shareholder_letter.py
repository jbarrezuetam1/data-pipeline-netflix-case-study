import pdfplumber

file_path = "week3-ingestion/raw_files/FINAL-Q2-26-Shareholder-Letter.pdf"

with pdfplumber.open(file_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")

    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        tables = page.find_tables()
        print(f"\n=== Page {i} ===")
        print(f"Tables found: {len(tables)}")
        print(f"Text preview (first 200 chars): {text[:200] if text else 'NO TEXT FOUND'}")
        