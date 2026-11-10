# 🐳 Docker Deployment for Company Knowledge Base RAG

## Quickstart
1. **Prepare configuration:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```
2. **Build and start container:**
   ```bash
   docker build -t company-rag .
   docker run -d -p 8501:8501 --env-file .env -v $(pwd)/documents:/app/documents company-rag
   ```
3. **Access Streamlit Web UI:**
   Open `http://localhost:8501` in your browser.
