# Company Knowledge Base RAG Chatbot

An internal AI assistant that answers employee questions based on company documents (PDF, Notion, Markdown, TXT) using **Retrieval-Augmented Generation (RAG)**.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Google API key (https://aistudio.google.com/apikey)
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY=...

# 3. Add documents to documents/ folder (PDF, .md, .txt)

# 4. Ingest documents into the vector store
python scripts/ingest.py

# 5. Run the chat UI
streamlit run app.py
```

## Project Structure

```
Rag/
├── app.py                 # Streamlit chat interface
├── config.py              # Configuration (paths, models, params)
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
├── README.md
├── docs/
│   └── ARCHITECTURE.md    # System architecture
├── src/
│   ├── document_loader.py # Load PDF, MD, TXT
│   ├── chunker.py         # Text chunking
│   ├── vectorstore.py     # FAISS indexing
│   ├── retriever.py       # Retrieval logic
│   └── chain.py           # RAG chain (retrieve + generate)
├── scripts/
│   └── ingest.py          # Ingest new documents
├── documents/             # Place your files here
└── vectorstore/           # FAISS index (created by ingest)
```

## Adding New Documents

1. Place new files in `documents/` (supports `.pdf`, `.md`, `.txt`)
2. Run ingestion:

   ```bash
   python scripts/ingest.py
   ```

3. Restart or refresh the Streamlit app

## Example Questions

- "How do I request vacation?"
- "Where is the backend coding standard?"
- "What is the onboarding process?"

## Tech Stack

- **Python** — Core language
- **LangChain** — RAG orchestration
- **FAISS** — Vector database
- **Google Gemini** — Embeddings + LLM
- **Streamlit** — Chat UI

## Configuration

| Variable        | Default                     | Description                  |
|----------------|-----------------------------|------------------------------|
| GOOGLE_API_KEY | —                           | Required                     |
| EMBEDDING_MODEL| models/text-embedding-004   | Embedding model              |
| LLM_MODEL      | gemini-1.5-flash            | Chat model                   |
| CHUNK_SIZE     | 1000                    | Characters per chunk         |
| CHUNK_OVERLAP  | 200                     | Overlap between chunks       |
| TOP_K_RETRIEVAL| 4                       | Chunks to retrieve per query |

## Production Improvements

1. **Authentication** — Add SSO/login for employees
2. **Incremental indexing** — Only re-ingest changed documents
3. **Re-ranking** — Use CrossEncoder for better relevance
4. **Persistent chat** — Store conversations in a database
5. **Monitoring** — Log queries, latency, feedback
6. **Hybrid search** — Combine vector + keyword (BM25)
7. **Cloud vector DB** — Pinecone/Qdrant for scale
# company-knowledge-base-rag
