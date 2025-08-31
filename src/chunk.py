# src/chunk.py
import os, json
from src.utils import ensure_dir, save_jsonl, load_jsonl, clean_text, text_hash

def _split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end]
        if end < L:
            back = chunk.rfind(". ")
            if back != -1 and back > len(chunk)//2:
                end = start + back + 2
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = max(end - chunk_overlap, end)
    return chunks

def make_chunks(pages_jsonl: str, out_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> str:
    ensure_dir(out_dir)
    pages = load_jsonl(pages_jsonl)
    rows = []
    chunk_id = 0
    for p in pages:
        txt = p.get("text", "") or ""
        parts = _split_text(txt, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for part in parts:
            chunk_id += 1
            rid = f"chunk_{chunk_id:06d}_{text_hash(part)}"
            rows.append({
                "chunk_id": rid,
                "text": clean_text(part),
                "pdf_path": p["pdf_path"],
                "page_start": p["page"],
                "page_end": p["page"],
                "is_scanned": p["is_scanned"],
            })
    chunks_jsonl = os.path.join(out_dir, "chunks.jsonl")
    save_jsonl(chunks_jsonl, rows)
    return chunks_jsonl
