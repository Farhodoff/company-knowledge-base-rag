"""
Ingest Script — Parse documents, generate embeddings, and build the FAISS vector index.
Usage:
    python scripts/ingest.py
    python scripts/ingest.py --dir /path/to/docs --chunk-size 800
"""

import sys
import time
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DOCUMENTS_DIR,
    VECTORSTORE_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
)
from src.document_loader import load_documents_from_directory
from src.chunker import chunk_documents
from src.vectorstore import create_vectorstore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def main():
    parser = argparse.ArgumentParser(description="Ingest company documents into FAISS vector database.")
    parser.add_argument("--dir", type=Path, default=DOCUMENTS_DIR, help="Path to documents folder.")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Maximum characters per chunk.")
    parser.add_argument("--chunk-overlap", type=int, default=CHUNK_OVERLAP, help="Overlap between chunks.")
    args = parser.parse_args()

    if not GOOGLE_API_KEY:
        print("\n❌ Error: GOOGLE_API_KEY is not set.")
        print("Please copy .env.example to .env and set your Google Gemini API key:")
        print("    cp .env.example .env")
        print("    echo 'GOOGLE_API_KEY=your_key_here' >> .env")
        print("Get your API key at: https://aistudio.google.com/apikey\n")
        sys.exit(1)

    print("=" * 60)
    print("🚀 Starting Company Knowledge Base Document Ingestion")
    print(f"📁 Target Folder : {args.dir}")
    print(f"🧠 Embeddings    : {EMBEDDING_MODEL}")
    print(f"✂️  Chunking     : size={args.chunk_size}, overlap={args.chunk_overlap}")
    print("=" * 60)

    start_time = time.time()

    # 1. Load documents
    print("\n[1/3] Scanning and loading documents...")
    documents = load_documents_from_directory(args.dir)
    if not documents:
        print(f"\n⚠️  No supported documents (.pdf, .md, .txt, .csv, .docx) found in: {args.dir}")
        print("Place your company policy files there and run this script again.")
        sys.exit(1)

    unique_files = sorted({d.metadata.get("filename", Path(d.metadata.get("source", "")).name) for d in documents})
    print(f"✅ Loaded {len(documents)} page(s)/file segment(s) across {len(unique_files)} document(s):")
    for f in unique_files:
        print(f"   • {f}")

    # 2. Chunk documents
    print("\n[2/3] Chunking documents into semantic fragments...")
    chunks = chunk_documents(documents, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    print(f"✅ Created {len(chunks)} text chunks.")

    # 3. Create Embeddings & FAISS Index
    print(f"\n[3/3] Generating vectors via {EMBEDDING_MODEL} and building FAISS index...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        transport="rest",
        request_timeout=90,
    )

    create_vectorstore(
        documents=chunks,
        embeddings=embeddings,
        persist_directory=VECTORSTORE_DIR,
        extra_metadata={
            "indexed_files": unique_files,
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
            "embedding_model": EMBEDDING_MODEL,
        },
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"🎉 Success! Vector store saved to: {VECTORSTORE_DIR}")
    print(f"⏱️  Total time: {elapsed:.2f}s")
    print("👉 Now start the chatbot UI with: streamlit run app.py")
    print("👉 Or test from terminal with: python scripts/query.py \"Your question here\"")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
