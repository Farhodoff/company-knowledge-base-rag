"""
Unit tests for Company Knowledge Base RAG components.
Run via: pytest tests/
"""

import sys
from pathlib import Path
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document
from src.chunker import chunk_documents
from src.document_loader import load_document, load_documents_from_directory
from src.chain import format_docs
from config import DOCUMENTS_DIR


def test_chunker_basic():
    """Verify chunker splits long text and attaches metadata properly."""
    long_text = "This is a sentence about company policy. " * 50
    doc = Document(page_content=long_text, metadata={"source": "test.md", "filename": "test.md"})
    
    chunks = chunk_documents([doc], chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert "chunk_index" in chunks[0].metadata
    assert chunks[0].metadata["filename"] == "test.md"


def test_chunker_empty_omitted():
    """Ensure whitespace-only chunks are discarded."""
    doc = Document(page_content="   \n\n   ", metadata={"source": "empty.md"})
    chunks = chunk_documents([doc], chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 0


def test_load_sample_markdown():
    """Verify loading real sample markdown documents."""
    sample_vacation = DOCUMENTS_DIR / "sample_vacation_policy.md"
    assert sample_vacation.exists()
    
    docs = load_document(sample_vacation)
    assert len(docs) >= 1
    assert "Vacation" in docs[0].page_content or "PTO" in docs[0].page_content
    assert docs[0].metadata["filename"] == "sample_vacation_policy.md"
    assert docs[0].metadata["extension"] == ".md"


def test_load_documents_from_directory():
    """Verify recursive directory loader aggregates existing documents."""
    docs = load_documents_from_directory(DOCUMENTS_DIR)
    assert len(docs) >= 4  # vacation, backend, onboarding, security
    filenames = {d.metadata.get("filename") for d in docs}
    assert "sample_vacation_policy.md" in filenames
    assert "sample_backend_standards.md" in filenames


def test_format_docs_citation():
    """Verify format_docs builds clear markdown source blocks."""
    docs = [
        Document(page_content="PTO is 24 days.", metadata={"filename": "vacation.md", "page": 1}),
        Document(page_content="Use feature branches.", metadata={"filename": "git.md", "page": 3}),
    ]
    formatted = format_docs(docs)
    assert "[Source: vacation.md (Page 1)]" in formatted
    assert "[Source: git.md (Page 3)]" in formatted
    assert "PTO is 24 days." in formatted
