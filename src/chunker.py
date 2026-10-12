"""
Text Chunker — Splits documents into overlapping semantic chunks for retrieval.
Uses RecursiveCharacterTextSplitter with hierarchy separators and chunk index tracking.
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """
    Split documents into overlapping chunks with clean metadata tracking.

    Args:
        documents: List of raw Document objects.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between adjacent chunks.

    Returns:
        List of chunked Document objects with preserved and enriched metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "### ", "## ", "# ", ". ", " ", ""],
    )

    raw_chunks = splitter.split_documents(documents)
    valid_chunks: List[Document] = []

    for idx, chunk in enumerate(raw_chunks):
        content = chunk.page_content.strip()
        if not content:
            continue
        chunk.page_content = content
        chunk.metadata["chunk_index"] = idx
        valid_chunks.append(chunk)

    return valid_chunks
