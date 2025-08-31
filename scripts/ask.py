# scripts/ask.py
import sys, os, time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag_pipeline import ask_ollama
from src.highlight import highlight_pdf

def main(pdf_path, query, k=5, llm="llama3.2"):
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    answer, results = ask_ollama(query, top_k=k, model=llm)
    print("\\n=== ANSWER ===\\n")
    print(answer)
    docs = results.get("documents", [])
    metas = results.get("metadatas", [])
    # Prepare evidence list for highlighting (top 3)
    evidences = []
    for d, m in zip(docs[:3], metas[:3]):
        evidences.append({"snippet": d, "page": m.get("page")})
    os.makedirs("outputs", exist_ok=True)
    out_pdf = os.path.join("outputs", f"annotated_{base}_{int(time.time())}.pdf")
    pages_jsonl = os.path.join("data", "processed", base, "pages.jsonl")
    highlight_pdf(pdf_path, pages_jsonl, evidences, out_pdf)
    print("\\nAnnotated PDF saved →", out_pdf)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python scripts\\ask.py data\\raw_pdfs\\your.pdf "Your question"')
    else:
        pdf = sys.argv[1]; q = " ".join(sys.argv[2:])
        main(pdf, q)
