from langchain_core.documents import Document
from src.chunker import chunk_documents

def test_chunker_overlap_consistency():
    text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 " * 20
    doc = Document(page_content=text, metadata={"source": "test.txt", "filename": "test.txt"})
    
    chunk_size = 100
    chunk_overlap = 25
    chunks = chunk_documents([doc], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    assert len(chunks) >= 2
    for i in range(len(chunks) - 1):
        # Current chunk end should share text with next chunk start
        tail = chunks[i].page_content[-20:].strip()
        head = chunks[i + 1].page_content[:40].strip()
        assert any(word in head for word in tail.split() if len(word) > 3)
