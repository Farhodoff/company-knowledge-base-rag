"""
Retriever — Configures similarity and MMR search strategies over the FAISS vector store.
"""

from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore


def get_retriever(
    vectorstore: VectorStore,
    top_k: int = 4,
    search_type: str = "similarity",
) -> BaseRetriever:
    """
    Create a retrieval interface from the vector store.

    Args:
        vectorstore: Initialized FAISS vector store.
        top_k: Number of most relevant chunks to retrieve.
        search_type: 'similarity' for standard cosine/L2, or 'mmr' for diverse retrieval.

    Returns:
        Configured BaseRetriever.
    """
    if search_type == "mmr":
        return vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": top_k, "fetch_k": max(top_k * 3, 10)},
        )

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
