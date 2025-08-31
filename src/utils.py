import os
import json
import fitz  # PyMuPDF

def load_jsonl(file_path):
    """
    Load JSONL file and return list of dictionaries.
    Each line in a .jsonl file is a valid JSON object.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                data.append(obj)
            except json.JSONDecodeError:
                continue  # skip invalid JSON lines
    return data


def ensure_dir(path):
    """
    Ensure that the directory for the given path exists.
    Example: ensure_dir("outputs/embeddings/index.faiss")
    This will create 'outputs/embeddings' if not exists.
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_pages(jsonl_path):
    """
    Read pages.jsonl and return list of page texts.
    This assumes each line has a JSON object with 'text' key.
    """
    pages = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            pages.append(obj.get("text", ""))
    return pages


def highlight_text_in_pdf(input_pdf, output_pdf, evidences):
    """
    Highlight snippets in the PDF and save to output.
    input_pdf: path to original pdf
    output_pdf: path to save highlighted pdf
    evidences: list of dicts like [{'snippet': 'text here', 'page': 3}, ...]
    """
    doc = fitz.open(input_pdf)

    for ev in evidences:
        snippet = (ev.get("snippet") or "").strip()
        page_num = int(ev.get("page", 1)) - 1  # fitz is 0-indexed
        if not snippet or page_num < 0 or page_num >= len(doc):
            continue
        page = doc[page_num]
        areas = page.search_for(snippet)
        for area in areas:
            highlight = page.add_highlight_annot(area)
            highlight.update()

    # Save annotated PDF
    doc.save(output_pdf, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_pdf
