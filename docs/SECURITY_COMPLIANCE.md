# 🔒 Enterprise Security & Data Governance FAQ

## Data Privacy
- **Are internal company documents used to train models?**  
  No. Documents are vectorized into a local FAISS index. Only relevant context chunks matching a specific employee query are sent to Google Gemini via secure TLS API calls, governed by enterprise non-training terms.
- **Where are vector embeddings stored?**  
  Locally inside `/vectorstore/faiss_index` on your private server or container volume. No third-party cloud vector database is required.

## Access Control (RBAC)
- Chunks can be tagged with departmental roles (`hr`, `finance`, `engineering`).
- Metadata filters ensure non-authorized personnel cannot retrieve restricted policy fragments.
