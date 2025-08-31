# scripts/batch_ingest.py
import os
from src.ingest import extract_pdf

RAW_DIR = "data/raw_pdfs"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

pdf_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(".pdf")]

for pdf in pdf_files:
    pdf_path = os.path.join(RAW_DIR, pdf)
    out_dir = os.path.join(PROCESSED_DIR, pdf.replace(".pdf", ""))
    pages_jsonl = extract_pdf(pdf_path, out_dir)
    print(f"✅ Processed: {pdf}, JSONL saved at {pages_jsonl}")
