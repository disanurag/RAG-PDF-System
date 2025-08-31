# scripts/batch_index.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.embed_index import build_index
from src.utils import ensure_dir

PROCESSED_DIR = "data/processed"
DB_DIR = "data/index/chroma"

ensure_dir(DB_DIR)

# Loop through all processed PDF folders
for folder in os.listdir(PROCESSED_DIR):
    folder_path = os.path.join(PROCESSED_DIR, folder)
    jsonl_path = os.path.join(folder_path, "pages.jsonl")
    
    if os.path.exists(jsonl_path):
        print(f"📌 Indexing PDF: {folder}")
        build_index(jsonl_path, pdf_id=folder)

print("✅ All PDFs indexed successfully into Chroma DB!")