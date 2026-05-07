import pdfplumber
import json
import sys

pdf_path = "3월_24일화_전국연합학력평가_감독배정표전학년_0317.pdf"

all_tables = []
try:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for obj in tables:
                all_tables.append(obj)
            print(f"Page {i+1} has {len(tables)} tables")
            
    with open("extracted_tables.json", "w", encoding="utf-8") as f:
        json.dump(all_tables, f, ensure_ascii=False, indent=2)
    print("Successfully extracted tables to extracted_tables.json")
except Exception as e:
    print(f"Error: {e}")
