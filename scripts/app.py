import sys, os
from pathlib import Path

# so that imports from src work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.rag_pipeline import answer_query

st.set_page_config(page_title="PDF RAG QA System", layout="wide")
st.title("📄 PDF RAG QA System")

proc_root = Path("data/processed")
folders = [p for p in sorted(proc_root.iterdir()) if p.is_dir() and (p / "pages.jsonl").exists()]

if not folders:
    st.warning("No processed PDFs found in data/processed. Run the indexing script first (scripts/build_index.py).")
    st.stop()

choices = {f.name: f for f in folders}
choice_name = st.selectbox("Choose a processed PDF", list(choices.keys()))
selected_folder = choices[choice_name]

query = st.text_input("Ask a question about the selected PDF")
top_k = st.slider("Number of snippets to retrieve (top-k)", min_value=1, max_value=5, value=3)

if st.button("Get Answer") and query.strip():
    with st.spinner("Running retrieval + LLM..."):
        try:
            answer, evidences, annotated_pdf_path = answer_query(selected_folder, query, top_k=top_k)
        except Exception as e:
            st.error(f"Error: {e}")
            raise

    st.subheader("✅ Answer")
    st.write(answer)

    st.subheader("📌 Top Evidence Snippets")
    for i, ev in enumerate(evidences, 1):
        snippet = (ev.get("snippet") or "").strip()
        st.markdown(f"**{i}. Page {ev.get('page', '?')}:** {snippet[:300]}...")

    if annotated_pdf_path and os.path.exists(annotated_pdf_path):
        with open(annotated_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="⬇️ Download Highlighted PDF",
            data=pdf_bytes,
            file_name=Path(annotated_pdf_path).name,
            mime="application/pdf"
        )
    else:
        st.error("Annotated PDF not found (highlight failed).")
