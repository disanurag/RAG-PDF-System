import os, json, time
from pathlib import Path
from src.embed_index import query_index
from src.highlight import highlight_pdf
import requests

# Ollama backend
OLLAMA_HOST = "http://localhost:11434"


def build_prompt(query: str, docs: list, metas: list, top_k: int = 3) -> str:
    blocks = []
    for i, (doc, meta) in enumerate(zip(docs[:top_k], metas[:top_k]), 1):
        page_no = meta.get("page") or meta.get("page_start") or "?"
        blocks.append(f"[Source {i} | p.{page_no}]: {doc.strip()}\n")
    context_text = "\n---\n".join(blocks)

    prompt = f"""
You are a helpful assistant that answers ONLY from the provided sources.
If the answer is not clearly present in the sources, say: "I don't know based on the provided documents."
Always add citations like [p.N] using the page numbers shown.

Question: {query}

Sources:
{context_text}

Answer (with citations):
"""
    return prompt.strip()


def generate_with_ollama(prompt: str, model: str = "llama3.2", timeout: int = 180) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data.get("response") or data.get("text") or str(data)


def ask_ollama(query: str, top_k: int = 3, model: str = "llama3.2"):
    res = query_index(query, top_k=top_k)
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]

    prompt = build_prompt(query, docs, metas, top_k=top_k)
    answer = generate_with_ollama(prompt, model=model)
    return answer, {"documents": docs, "metadatas": metas, "distances": distances}


def answer_query(processed_folder: str | Path, query: str, top_k: int = 3, model: str = "llama3.2"):
    processed_folder = Path(processed_folder)
    pages_jsonl = processed_folder / "pages.jsonl"
    if not pages_jsonl.exists():
        raise FileNotFoundError(f"pages.jsonl not found at: {pages_jsonl}")

    # detect original PDF path
    with open(pages_jsonl, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        if not first:
            raise ValueError("pages.jsonl is empty")
        info = json.loads(first)
        pdf_path = info.get("pdf_path")

    if not pdf_path or not Path(pdf_path).exists():
        cand = list(processed_folder.glob("*.pdf"))
        if cand:
            pdf_path = str(cand[0])
        else:
            raw_cand = Path("data/raw_pdfs") / f"{processed_folder.name}.pdf"
            if raw_cand.exists():
                pdf_path = str(raw_cand)
            else:
                raise FileNotFoundError("Cannot find original PDF for processed folder: " + str(processed_folder))

    # 1) LLM query
    answer, results = ask_ollama(query, top_k=top_k, model=model)

    # 2) evidences
    docs = results.get("documents", [])
    metas = results.get("metadatas", [])
    evidences = []
    for d, m in zip(docs[:top_k], metas[:top_k]):
        page_no = m.get("page") or m.get("page_start") or 1
        evidences.append({"snippet": d, "page": int(page_no)})

    # 3) highlight and save
    os.makedirs("outputs", exist_ok=True)
    out_pdf = os.path.join("outputs", f"annotated_{processed_folder.name}_{int(time.time())}.pdf")
    highlight_pdf(pdf_path, str(pages_jsonl), evidences, out_pdf)

    return answer, evidences, out_pdf
