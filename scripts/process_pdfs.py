import os
from src.highlight import extract_pages_metadata  

pdf_dir = "data/raw_pdfs"
processed_dir = "data/processed"

for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        out_folder = os.path.join(processed_dir, pdf_file.replace(".pdf",""))
        os.makedirs(out_folder, exist_ok=True)
        pages_jsonl = os.path.join(out_folder, "pages.jsonl")
        extract_pages_metadata(pdf_path, pages_jsonl)
        print(f"Processed {pdf_file}")
