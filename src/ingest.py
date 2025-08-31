# src/ingest.py
import os, io, json
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
from tqdm import tqdm
from src.utils import ensure_dir, save_jsonl, clean_text

# ⚠️ Windows users ke liye important:
# Agar tesseract PATH me nahi hai, to full path yahan set karo.
# Install hone ke baad default path usually yeh hota hai:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_pdf(pdf_path: str, out_dir: str, ocr_dpi: int = 300) -> str:
    ensure_dir(out_dir)
    pages_jsonl = os.path.join(out_dir, "pages.jsonl")
    ocr_dir = os.path.join(out_dir, "ocr")
    ensure_dir(ocr_dir)

    doc = fitz.open(pdf_path)
    rows = []
    for i in tqdm(range(len(doc)), desc=f"Ingesting {os.path.basename(pdf_path)}"):
        page = doc[i]
        text = page.get_text("text") or ""
        text = text.strip()
        is_scanned = (len(text) < 20)  # heuristic

        page_entry = {
            "pdf_path": os.path.abspath(pdf_path),
            "page": i + 1,
            "n_pages": len(doc),
            "is_scanned": bool(is_scanned),
            "text": "",
            "ocr": None,
        }

        if not is_scanned:
            page_entry["text"] = clean_text(text)
        else:
            zoom = ocr_dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            img_path = os.path.join(ocr_dir, f"page_{i+1}.png")
            img.save(img_path)

            data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)
            words = []
            tokens = []
            n = len(data.get("text", []))
            for j in range(n):
                wtxt = (data["text"][j] or "").strip()
                if not wtxt:
                    continue
                left, top, width, height = data["left"][j], data["top"][j], data["width"][j], data["height"][j]
                words.append({
                    "text": wtxt,
                    "bbox": [left/zoom, top/zoom, (left+width)/zoom, (top+height)/zoom]
                })
                tokens.append(wtxt)
            page_entry["text"] = clean_text(" ".join(tokens))
            page_entry["ocr"] = {"image_path": img_path, "zoom": zoom, "words": words}

        rows.append(page_entry)

    save_jsonl(pages_jsonl, rows)
    return pages_jsonl
