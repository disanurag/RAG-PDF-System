# src/embed_index.py
import os
from sentence_transformers import SentenceTransformer
import chromadb
from src.utils import load_jsonl, ensure_dir

# -------------------------
# Chroma DB Settings
# -------------------------
CHROMA_DIR = "data/index/chroma"

# Initialize Chroma persistent client
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="pdf_chunks")

# -------------------------
# Sentence Transformer model
# -------------------------
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# -------------------------
# Build index from JSONL
# -------------------------
def build_index(chunks_jsonl: str, pdf_id: str):
    """
    Build embeddings for each page/chunk and add to Chroma collection.
    Compatible with pages.jsonl from ingest.py
    """
    ensure_dir(CHROMA_DIR)
    chunks = load_jsonl(chunks_jsonl)

    texts = [c.get("text", "") for c in chunks]
    ids = [f"{pdf_id}_{i}" for i in range(len(texts))]
    
    # Fix missing keys: use 'page' if 'page_start' not available, 'chunk_id' default 0
    metas = [
        {
            "page": c.get("page", 1),
            "chunk_id": c.get("chunk_id", 0),
            "pdf_path": c.get("pdf_path", "")
        } 
        for c in chunks
    ]

    # Encode in batches to save memory
    batch_size = 64
    embs = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embs = embed_model.encode(batch_texts, convert_to_numpy=True, normalize_embeddings=True)
        embs.extend(batch_embs.tolist())

    # Add to Chroma collection
    collection.add(ids=ids, documents=texts, metadatas=metas, embeddings=embs)
    print(f"✅ Indexed {len(texts)} pages/chunks into Chroma at {CHROMA_DIR}")

# -------------------------
# Query Chroma index
# -------------------------
def query_index(query: str, top_k: int = 5):
    """
    Query Chroma collection using sentence embedding similarity
    Returns top_k documents with metadata
    """
    q_emb = embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True).tolist()
    results = collection.query(query_embeddings=q_emb, n_results=top_k)
    return results