# Company Knowledge Base RAG Chatbot — System Architecture

## Overview

This system enables employees to ask questions about company documents and receive AI-generated answers grounded in retrieved context.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGEST PIPELINE (One-time / Scheduled)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PDF] [Notion] [MD] [TXT]  ──►  Document Loader  ──►  Text Chunker         │
│                                          │                      │           │
│                                          ▼                      ▼           │
│                                  OpenAI Embeddings  ◄──  Chunks             │
│                                          │                                   │
│                                          ▼                                   │
│                                  FAISS Vector Store                         │
│                                          │                                   │
└──────────────────────────────────────────┼───────────────────────────────────┘
                                           │
┌──────────────────────────────────────────┼───────────────────────────────────┐
│                           QUERY PIPELINE (Per Question)                      │
├──────────────────────────────────────────┼───────────────────────────────────┤
│                                          ▼                                   │
│  [User Question]  ──►  Embed Question  ──►  Similarity Search (FAISS)       │
│                                                      │                       │
│                                                      ▼                       │
│                                              Retrieved Chunks                │
│                                                      │                       │
│                                                      ▼                       │
│  [Streamlit UI]  ◄──  Answer  ◄──  LLM  ◄──  Prompt(Context + Question)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Responsibility |
|-----------|----------------|
| **Document Loader** | Load PDF, MD, TXT, Notion exports; normalize to text |
| **Chunker** | Split text into overlapping chunks for retrieval |
| **Embeddings** | Convert chunks to vectors via OpenAI |
| **Vector Store** | FAISS index for similarity search |
| **Retriever** | Fetch top-K relevant chunks for a question |
| **RAG Chain** | Combine retrieval + LLM generation |
| **Streamlit UI** | Chat interface + source citations |

## Data Flow

1. **Ingest**: Documents → Parse → Chunk → Embed → FAISS index
2. **Query**: Question → Embed → Search FAISS → Top-K chunks
3. **Generate**: Chunks + Question → LLM → Answer + Sources
