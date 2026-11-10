"""
Retriever — Configures similarity, MMR, and Hybrid (Dense + Sparse) search strategies.
"""

from typing import List, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document


def get_retriever(
    vectorstore: VectorStore,
    top_k: int = 4,
    search_type: str = "similarity",
) -> BaseRetriever:
    """
    Create a standard retrieval interface from the vector store.

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


def get_hybrid_retriever(
    vectorstore: VectorStore,
    documents: Optional[List[Document]] = None,
    top_k: int = 4,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> BaseRetriever:
    """
    Build a hybrid ensemble retriever (Dense Vector + BM25 Sparse Keyword).
    Falls back gracefully to dense vector retrieval if BM25 is unavailable or documents are empty.
    """
    dense_retriever = get_retriever(vectorstore, top_k=top_k)

    if not documents:
        return dense_retriever

    try:
        from langchain_community.retrievers import BM25Retriever
        from langchain.retrievers import EnsembleRetriever

        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = top_k

        return EnsembleRetriever(
            retrievers=[dense_retriever, bm25_retriever],
            weights=[dense_weight, sparse_weight],
        )
    except Exception:
        # Fallback to standard dense retrieval when optional dependencies aren't present
        return dense_retriever
