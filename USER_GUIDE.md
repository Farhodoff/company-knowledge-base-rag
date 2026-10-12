# 🏢 Company Knowledge Base RAG — Comprehensive User Guide & Docs

Welcome to the official documentation and user handbook for **Company Knowledge Base RAG**, an enterprise-grade, local-first Question-Answering system grounded strictly in internal corporate documentation.

---

## 📑 Table of Contents
1. [Overview & Core Value](#1-overview--core-value)
2. [Quick Installation (macOS & Linux)](#2-quick-installation-macos--linux)
3. [API Key Setup (`GOOGLE_API_KEY`)](#3-api-key-setup)
4. [Document Management (PDF, Markdown, CSV, DOCX)](#4-document-management)
5. [Global Terminal CLI (`company-rag`)](#5-global-terminal-cli)
6. [Streamlit Web Cockpit Guide](#6-streamlit-web-cockpit-guide)
7. [Enterprise Integrations (Slack, Discord, REST API)](#7-enterprise-integrations)
8. [Architecture & Retrieval Deep-Dive](#8-architecture--retrieval-deep-dive)
9. [Troubleshooting & FAQ](#9-troubleshooting--faq)

---

## 1. Overview & Core Value
Standard LLMs hallucinate internal company policies and invent answers based on public internet data. **Company Knowledge Base RAG** eliminates this problem:

- **100% Grounded Answers**: Synthesizes responses exclusively from ingested corporate files.
- **Verifiable Citations**: Every claim is annotated with the source file and page index (e.g., `sample_engineering_handbook.pdf (Page 4)`).
- **Zero Hallucination Guardrails**: Explicitly refuses to guess when documentation does not contain the answer.
- **Local-First Vector Space**: Encodes embeddings into an on-premise FAISS index without third-party vector SaaS locks.

---

## 2. Quick Installation (macOS & Linux)

###  1-Line Terminal Auto-Installer
Run the following command in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Farhodoff/company-knowledge-base-rag/main/install.sh | bash
```

**The installer automatically:**
1. Clones the repository into `~/.company-rag`.
2. Creates an isolated virtual environment (`.venv`) and installs optimized dependencies.
3. Symlinks the global CLI executable to `~/.local/bin/company-rag`.
4. Compiles a native macOS desktop launcher at `~/Applications/Company Knowledge Base.app`.

> **Note:** If `company-rag` is not immediately found in your terminal, restart your shell or run `export PATH="$HOME/.local/bin:$PATH"`.

---

## 3. API Key Setup

The system uses Google Gemini for high-density embeddings and strict grounded response generation. Obtain a key from [Google AI Studio](https://aistudio.google.com/apikey).

### Save Key via CLI:
```bash
company-rag config YOUR_GEMINI_API_KEY
```
or:
```bash
company-rag set-key YOUR_GEMINI_API_KEY
```

*This command automatically updates your `.env` configuration and triggers document vectorization immediately.*

---

## 4. Document Management

Supported formats:
- **PDF**: Engineering handbooks, benefits guides, architecture specs (`.pdf`)
- **Markdown / Text**: Coding guidelines, runbooks, README files (`.md`, `.txt`)
- **Word Documents**: Formal HR policies, onboarding manuals (`.docx`)
- **CSV**: Department rosters, team contacts (`.csv`)

### Adding Documents:
```bash
# Add a new PDF to the archive and re-index:
company-rag add ~/Downloads/2026_engineering_standards.pdf

# Open documents folder directly in macOS Finder:
company-rag docs
```

### Manual Batch Ingestion:
```bash
company-rag ingest
```

---

## 5. Global Terminal CLI (`company-rag`)

Query internal knowledge without ever opening a web browser:

| Command | Description |
|---|---|
| `company-rag ask "<question>"` | Direct question answering with citations in terminal |
| `company-rag ui` | Launch the Streamlit dashboard in default browser |
| `company-rag add <file>` | Copy new document and re-index automatically |
| `company-rag ingest` | Full batch re-indexing of `documents/` folder |
| `company-rag docs` | Open `documents/` folder in macOS Finder |
| `company-rag config [KEY]` | Set Google API Key or edit `.env` parameters |
| `company-rag update` | Pull latest updates from GitHub |
| `company-rag slack` | Start Slack Bot (Socket Mode) |
| `company-rag discord` | Start Discord Bot client |
| `company-rag api [--port 8000]` | Start universal REST Webhook server |

---

## 6. Streamlit Web Cockpit Guide

### Launching:
```bash
company-rag ui
```
or press `Cmd + Space` (Spotlight) and search for **"Company Knowledge Base"**.

### Features:
1. **🌐 Bilingual Toggle**: Switch seamlessly between 🇺🇿 O‘zbekcha and 🇬🇧 English in the sidebar.
2. **One-Click Quick Prompts**: Instant queries for Vacation, Backend Standards, Onboarding, and Security.
3. **Drag & Drop Upload**: Upload company documents directly through the web interface.
4. **Verified Sources Inspector**: Expand retrieved chunks with highlighted citations and page numbers.
5. **Model Controls**: Choose LLM model (`gemini-2.5-flash`), adjust temperature, and tune Top-K retrieval chunks.

---

## 7. Enterprise Integrations

### 1. Slack Bot (Socket Mode)
Respond to `@KnowledgeBot` mentions inside company channels with Block Kit citations:
```bash
company-rag slack
```
*Operates behind corporate firewalls without requiring public webhooks.*

### 2. Discord Bot
Deploy in engineering Discord servers using `!ask <query>`:
```bash
company-rag discord
```

### 3. Universal REST Webhook API
Integrate with internal portals, wikis, or Zapier automation:
```bash
company-rag api --port 8000
```
**Example cURL Query:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is our code review policy?"}'
```

---

## 8. Troubleshooting & FAQ

### ❓ `command not found: company-rag`
Ensure `~/.local/bin` is in your environment PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### ❓ `404 NOT_FOUND` for Embedding Model
Ensure your configuration points to current models:
```bash
EMBEDDING_MODEL=models/gemini-embedding-001
LLM_MODEL=gemini-2.5-flash
```

---

**Author**: Farhod ([GitHub: @Farhodoff](https://github.com/Farhodoff))  
**License**: MIT License
