"""
Retriever — Retrieves relevant chunks from the vector store.
"""

from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore


def get_retriever(vectorstore: VectorStore, top_k: int = 4) -> BaseRetriever:
    """
    Create a retriever from the vector store.

    Args:
        vectorstore: FAISS vector store.
        top_k: Number of chunks to retrieve per query.

    Returns:
        Retriever instance.
    """
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
