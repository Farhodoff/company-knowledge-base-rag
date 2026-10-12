"""
Document Loader — Loads documents from PDF, Markdown, TXT, DOCX, and CSV formats.
Enriches each document with source metadata for precise citations.
"""

import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt", ".csv", ".docx"}


def load_document(file_path: Path) -> List[Document]:
    """
    Load a single document based on file extension with source tracking.

    Args:
        file_path: Path to the target document.

    Returns:
        List of Document objects with clean content and metadata.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Document file does not exist: {file_path}")

    suffix = file_path.suffix.lower()
    base_meta = {
        "source": str(file_path),
        "filename": file_path.name,
        "extension": suffix,
        "size_bytes": file_path.stat().st_size,
    }

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        for i, doc in enumerate(docs):
            doc.metadata.update(base_meta)
            doc.metadata["page"] = i + 1
        return docs

    if suffix in (".md", ".markdown", ".txt"):
        loader = TextLoader(str(file_path), encoding="utf-8", autodetect_encoding=True)
        docs = loader.load()
        for doc in docs:
            doc.metadata.update(base_meta)
            doc.metadata["page"] = 1
        return docs

    if suffix == ".csv":
        loader = CSVLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
        for i, doc in enumerate(docs):
            doc.metadata.update(base_meta)
            doc.metadata["row"] = i + 1
            doc.metadata["page"] = 1
        return docs

    if suffix == ".docx":
        try:
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata.update(base_meta)
                doc.metadata["page"] = 1
            return docs
        except ImportError:
            # Fallback if docx2txt is not installed
            logger.warning("docx2txt not installed; skipping %s", file_path.name)
            return []

    raise ValueError(f"Unsupported document format '{suffix}'. Supported: {SUPPORTED_EXTENSIONS}")


def load_documents_from_directory(directory: Path) -> List[Document]:
    """
    Scan and load all supported documents recursively from a directory.
    Skips unreadable or corrupted files gracefully without aborting the batch.

    Args:
        directory: Path to folder containing source documents.

    Returns:
        Aggregated list of loaded Document objects.
    """
    if not directory.exists() or not directory.is_dir():
        logger.warning("Directory %s does not exist or is not a directory.", directory)
        return []

    all_docs: List[Document] = []
    supported_files = [
        p for p in directory.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS and not p.name.startswith(".")
    ]

    for file_path in sorted(supported_files):
        try:
            docs = load_document(file_path)
            all_docs.extend(docs)
            logger.info("Successfully loaded %s (%d document segment/pages)", file_path.name, len(docs))
        except Exception as exc:
            logger.error("Failed to load document %s: %s", file_path, exc)

    return all_docs
