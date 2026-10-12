"""
Vector Store — FAISS indexing, metadata tracking, and persistence.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def vectorstore_exists(persist_directory: Path) -> bool:
    """Check if a saved FAISS index exists in the target directory."""
    index_file = persist_directory / "index.faiss"
    pkl_file = persist_directory / "index.pkl"
    return index_file.exists() and pkl_file.exists()


def create_vectorstore(
    documents: List[Document],
    embeddings: Embeddings,
    persist_directory: Path,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> FAISS:
    """
    Create a FAISS vector store from document chunks and persist to disk.

    Args:
        documents: Chunked Document objects.
        embeddings: Embedding model instance.
        persist_directory: Destination folder for the FAISS index.
        extra_metadata: Optional dictionary with ingestion statistics.

    Returns:
        Instantiated FAISS vector store.
    """
    persist_directory.mkdir(exist_ok=True, parents=True)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(persist_directory))

    # Save manifest for auditing and UI display
    manifest_data: Dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_chunks": len(documents),
        "unique_sources": len({d.metadata.get("filename", d.metadata.get("source", "")) for d in documents}),
    }
    if extra_metadata:
        manifest_data.update(extra_metadata)

    manifest_path = persist_directory / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return vectorstore


def load_vectorstore(
    persist_directory: Path,
    embeddings: Embeddings,
) -> FAISS:
    """
    Load an existing FAISS vector store from disk.

    Args:
        persist_directory: Folder containing FAISS index.faiss and index.pkl.
        embeddings: Same embedding model instance used during creation.

    Returns:
        Loaded FAISS vector store.
    """
    if not vectorstore_exists(persist_directory):
        raise FileNotFoundError(f"FAISS index not found at {persist_directory}")

    return FAISS.load_local(
        str(persist_directory),
        embeddings,
        allow_dangerous_deserialization=True,
    )
