# PDF Retrieval-Augmented Generation (RAG) System

## Project Overview
This project is an **end-to-end Retrieval-Augmented Generation (RAG) system** for PDF documents.  
It can:
- Ingest PDF files (both native and scanned)
- Perform chunking of text
- Generate embeddings using SentenceTransformers
- Build a local ChromaDB index
- Answer user queries using LLaMA3 with top-k retrieval
- Highlight evidence in original PDFs
- Optional Streamlit web UI for interactive queries

## Features
- Local-only execution (no cloud APIs required)
- Handles scanned PDFs with OCR
- Configurable chunk size and top-k retrieval
- Generates answers with citations `[p.N]`
- Optional highlighted annotated PDF output
- Optional Streamlit UI for demo

## Directory Structure
aavtaar_rag/
├── data/
│ ├── raw_pdfs/ # Input PDFs
│ ├── processed/ # Extracted pages + chunks
│ └── index/chroma/ # ChromaDB embeddings
├── scripts/
│ ├── build_index.py
│ ├── batch_index.py
│ └── generate_hld_pdf.py
├── src/
│ ├── ingest.py
│ ├── chunk.py
│ ├── embed_index.py
│ ├── rag_pipeline.py
│ └── highlight.py
├── .gitignore
├── README.md
└── requirements.txt


## Installation
1. Clone the repository:
git clone <https://github.com/disanurag/RAG-PDF-System.git>
cd aavtaar_rag

2. Create a virtual environment:
python -m venv .venv

3. Activate the virtual environment:
Windows

.venv\Scripts\Activate.ps1

Linux/Mac

source .venv/bin/activate

4. Install dependencies:
pip install -r requirements.txt

## Usage

### Build index for a single PDF
python scripts/build_index.py data/raw_pdfs/your_pdf_file.pdf

### Build index for all PDFs in batch
python scripts/batch_index.py

### Generate High-Level Design PDF
python scripts/generate_hld_pdf.py

### Streamlit Web UI (Optional)
streamlit run src/app.py

## Deliverables
- **HLD Document:** `HLD_PDF_RAG_System.pdf`
- **Source Code:** `src/` + `scripts/`
- **Indexed Data:** `data/processed/` & ChromaDB (`data/index/chroma/`)
- **Demo Video:** Short screen recording showing end-to-end workflow

## GitHub Push Steps
git init
git add .
git commit -m "Initial commit - PDF RAG System"
git branch -M main
git remote add origin <https://github.com/disanurag/RAG-PDF-System.git>
git push -u origin main
