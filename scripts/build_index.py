# scripts/build_index.py
import sys, os
# ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest import extract_pdf
from src.chunk import make_chunks
from src.embed_index import build_index

def main(pdf_path):
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.join("data", "processed", base)
    os.makedirs(out_dir, exist_ok=True)

    print("📥 Extracting PDF...")
    pages_jsonl = extract_pdf(pdf_path, out_dir)

    print("✂️  Chunking text...")
    chunks_jsonl = make_chunks(pages_jsonl, out_dir)

    print("📦 Building index...")
    build_index(chunks_jsonl, base)

    print("✅ Build finished for", pdf_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts\\build_index.py data\\raw_pdfs\\your.pdf")
    else:
        main(sys.argv[1])
