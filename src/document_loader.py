"""
Document Loader — Loads documents from PDF, Markdown, TXT, and Notion exports.
Uses LangChain document loaders with metadata for source tracking.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


def load_document(file_path: Path) -> List[Document]:
    """
    Load a single document based on file extension.

    Args:
        file_path: Path to the document file.

    Returns:
        List of Document objects with content and metadata.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        # Add source path to metadata for each page
        for i, doc in enumerate(docs):
            doc.metadata["source"] = str(file_path)
            doc.metadata["page"] = i + 1
        return docs

    if suffix in (".md", ".markdown"):
        loader = TextLoader(str(file_path), encoding="utf-8", autodetect_encoding=True)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = str(file_path)
        return docs

    if suffix == ".txt":
        loader = TextLoader(str(file_path), encoding="utf-8", autodetect_encoding=True)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = str(file_path)
        return docs

    raise ValueError(f"Unsupported file type: {suffix}")


def load_documents_from_directory(directory: Path) -> List[Document]:
    """
    Load all supported documents from a directory (recursive).

    Supported: .pdf, .md, .markdown, .txt

    Args:
        directory: Path to directory containing documents.

    Returns:
        List of Document objects from all files.
    """
    supported = {".pdf", ".md", ".markdown", ".txt"}
    all_docs: List[Document] = []

    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported:
            try:
                docs = load_document(file_path)
                all_docs.extend(docs)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

    return all_docs
