"""
Vector Store — FAISS indexing and persistence.
Stores embeddings for similarity search.
"""

from pathlib import Path
from typing import List, Optional

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore


def create_vectorstore(
    documents: List[Document],
    embeddings: Embeddings,
    persist_directory: Path,
) -> FAISS:
    """
    Create a FAISS vector store from documents and persist to disk.

    Args:
        documents: Chunked documents.
        embeddings: Embedding model.
        persist_directory: Path to save FAISS index.

    Returns:
        FAISS vector store.
    """
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(persist_directory))
    return vectorstore


def load_vectorstore(
    persist_directory: Path,
    embeddings: Embeddings,
) -> FAISS:
    """
    Load an existing FAISS vector store from disk.

    Args:
        persist_directory: Path containing FAISS index.
        embeddings: Same embedding model used at creation.

    Returns:
        FAISS vector store.
    """
    return FAISS.load_local(
        str(persist_directory),
        embeddings,
        allow_dangerous_deserialization=True,
    )
