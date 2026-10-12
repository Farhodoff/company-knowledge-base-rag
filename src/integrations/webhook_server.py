"""
Universal Webhook & REST Server — Lightweight API endpoint for external integrations.
Accepts POST requests from Slack webhooks, Discord webhooks, or internal company portals.

Usage:
    python src/integrations/webhook_server.py --port 8000
"""

import sys
import json
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    VECTORSTORE_DIR,
    TOP_K_RETRIEVAL,
    SEARCH_TYPE,
    GOOGLE_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    TEMPERATURE,
)
from src.vectorstore import load_vectorstore, vectorstore_exists
from src.retriever import get_retriever
from src.chain import create_rag_chain_with_sources
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

_rag_cache = None


def get_rag():
    global _rag_cache
    if _rag_cache is None:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set.")
        if not vectorstore_exists(VECTORSTORE_DIR):
            raise FileNotFoundError(f"Vector store not found at {VECTORSTORE_DIR}")

        embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
            transport="rest",
        )
        vectorstore = load_vectorstore(VECTORSTORE_DIR, embeddings)
        retriever = get_retriever(vectorstore, top_k=TOP_K_RETRIEVAL, search_type=SEARCH_TYPE)
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            transport="rest",
        )
        _rag_cache = create_rag_chain_with_sources(llm, retriever)
    return _rag_cache


class RAGWebhookHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/health", "/api/v1/health"):
            ready = vectorstore_exists(VECTORSTORE_DIR)
            self._send_json(200, {"status": "ok", "vectorstore_ready": ready})
        else:
            self._send_json(404, {"error": "Not Found. Use POST /api/v1/query or GET /health"})

    def do_POST(self):
        if self.path in ("/query", "/api/v1/query"):
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json(400, {"error": "Missing JSON request body"})
                return

            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._send_json(400, {"error": "Invalid JSON format"})
                return

            question = payload.get("question") or payload.get("text") or payload.get("prompt")
            if not question:
                self._send_json(400, {"error": "Field 'question' is required"})
                return

            try:
                rag = get_rag()
                answer, sources = rag(question)
                formatted_sources = [
                    {
                        "filename": d.metadata.get("filename", Path(d.metadata.get("source", "")).name),
                        "page": d.metadata.get("page", 1),
                        "excerpt": d.page_content[:200],
                    }
                    for d in sources
                ]
                self._send_json(200, {
                    "question": question,
                    "answer": answer,
                    "sources": formatted_sources,
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not Found"})


def main():
    parser = argparse.ArgumentParser(description="Universal RAG Webhook Server")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    args = parser.parse_args()

    server_address = ("", args.port)
    httpd = HTTPServer(server_address, RAGWebhookHandler)
    print(f"🚀 RAG Webhook Server running on http://0.0.0.0:{args.port}")
    print("👉 Endpoints:")
    print(f"   • POST http://localhost:{args.port}/api/v1/query (JSON: {{\"question\": \"...\"}})")
    print(f"   • GET  http://localhost:{args.port}/health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
