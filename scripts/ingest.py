"""
Ingest Script — Add new documents to the vector store.
Run: python scripts/ingest.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / ".env")

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


def ingest():
    """Load documents, chunk, embed, and save to FAISS."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set. Add it to .env")
        sys.exit(1)

    print(f"Loading documents from {DOCUMENTS_DIR}...")
    documents = load_documents_from_directory(DOCUMENTS_DIR)

    if not documents:
        print("No documents found. Add PDF, MD, or TXT files to documents/")
        sys.exit(1)

    print(f"Loaded {len(documents)} document(s)")

    print("Chunking...")
    chunks = chunk_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"Created {len(chunks)} chunks")

    print("Creating embeddings and FAISS index...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        transport="rest",
        request_timeout=60,
    )
    vectorstore = create_vectorstore(chunks, embeddings, VECTORSTORE_DIR)

    print(f"Saved vector store to {VECTORSTORE_DIR}")
    print("Done.")


if __name__ == "__main__":
    ingest()
