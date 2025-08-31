import fitz  # PyMuPDF
import json
import os


def highlight_pdf(input_pdf: str, pages_jsonl: str, evidences: list, output_pdf: str):
    """
    Highlights text in a PDF based on evidence snippets.

    Args:
        input_pdf (str): Path to the original PDF.
        pages_jsonl (str): Path to the pages.jsonl file (OCR/parsed data).
        evidences (list): List of dicts with keys 'snippet' and 'page'.
        output_pdf (str): Path where the highlighted PDF will be saved.
    """

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"PDF not found: {input_pdf}")
    if not os.path.exists(pages_jsonl):
        raise FileNotFoundError(f"pages.jsonl not found: {pages_jsonl}")

    # Load page metadata
    pages = []
    with open(pages_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            try:
                pages.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    # Open PDF
    doc = fitz.open(input_pdf)

    for ev in evidences:
        ev_text = ev.get("snippet") or ev.get("text")  # fix: use snippet from rag_pipeline
        ev_page = ev.get("page")

        if not ev_text or ev_page is None:
            continue

        try:
            page_num = int(ev_page) - 1  # fix: rag_pipeline gives 1-based, fitz is 0-based
        except Exception:
            continue

        if page_num < 0 or page_num >= len(doc):
            continue

        page = doc[page_num]

        # --- Meta info (optional OCR words) ---
        meta = pages[page_num] if page_num < len(pages) else None

        # --- Try native text search ---
        areas = page.search_for(ev_text)
        if areas:
            for rect in areas:
                highlight = page.add_highlight_annot(rect)
                highlight.update()
            continue

        # --- Fallback: OCR word-level search ---
        if meta and "ocr" in meta and isinstance(meta["ocr"], dict) and "words" in meta["ocr"]:
            words = meta["ocr"]["words"]
            for w in words:
                if ev_text.lower() in w.get("text", "").lower():
                    bbox = w.get("bbox")
                    if bbox:
                        rect = fitz.Rect(bbox)
                        highlight = page.add_highlight_annot(rect)
                        highlight.update()

    # Save highlighted PDF
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_pdf
