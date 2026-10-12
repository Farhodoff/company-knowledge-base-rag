"""
CLI Query Tool — Test questions directly against the knowledge base from terminal.
Usage:
    python scripts/query.py "How do I request vacation days?"
    python scripts/query.py --top-k 3 "What is the git branching policy?"
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
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


def main():
    parser = argparse.ArgumentParser(description="Query the company knowledge base from CLI.")
    parser.add_argument("question", type=str, nargs="?", help="Question to ask the AI assistant.")
    parser.add_argument("--query", "-q", type=str, dest="query_flag", help="Question query flag.")
    parser.add_argument("--top-k", type=int, default=TOP_K_RETRIEVAL, help="Number of retrieved chunks.")
    parser.add_argument("--model", type=str, default=LLM_MODEL, help="Gemini chat model.")
    parser.add_argument("--mock", "--dry-run", action="store_true", help="Simulate retrieval and response for offline testing.")
    args = parser.parse_args()

    question = args.question or args.query_flag
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()

    # Interactive prompt if no question argument passed
    if not question:
        try:
            question = input("\n💬 Enter your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    if not question:
        print("No question provided.")
        sys.exit(0)

    if args.mock:
        print(f"\n🧪 [MOCK MODE] Simulating RAG retrieval for: \"{question}\" (top_k={args.top_k})...\n")
        print("=" * 60)
        print("💡 Answer (Mock Simulation):")
        print(f"Based on internal documents, full-time employees receive 24 days of paid time off (PTO) annually.")
        print("All leave requests must be submitted at least 2 weeks in advance via BambooHR.")
        print("=" * 60)
        print("\n📚 Sources:")
        print("  • sample_vacation_policy.md (Page 1)")
        print("    Excerpt: 'All full-time employees accrue 24 days of PTO per calendar year...'")
        print("=" * 60)
        return

    if not GOOGLE_API_KEY:
        print("\n❌ Error: GOOGLE_API_KEY is not set in environment or .env file.")
        print("Tip: You can run with `--mock` to verify the CLI pipeline without an API key.\n")
        sys.exit(1)

    if not vectorstore_exists(VECTORSTORE_DIR):
        print(f"\n❌ Error: Vector store not found at {VECTORSTORE_DIR}")
        print("Run ingestion first: python scripts/ingest.py\n")
        sys.exit(1)

    print(f"\n🔍 Searching knowledge base for: \"{question}\" (top_k={args.top_k}, model={args.model})...\n")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        transport="rest",
    )
    vectorstore = load_vectorstore(VECTORSTORE_DIR, embeddings)
    retriever = get_retriever(vectorstore, top_k=args.top_k, search_type=SEARCH_TYPE)

    llm = ChatGoogleGenerativeAI(
        model=args.model,
        google_api_key=GOOGLE_API_KEY,
        temperature=TEMPERATURE,
        transport="rest",
    )

    rag = create_rag_chain_with_sources(llm, retriever)
    answer, sources = rag(question)

    print("=" * 60)
    print("🤖 ASSISTANT ANSWER:")
    print("=" * 60)
    print(answer)
    print("\n" + "-" * 60)
    print("📎 SOURCES CONSULTED:")
    print("-" * 60)
    if not sources:
        print("No matching documents found.")
    else:
        for i, doc in enumerate(sources, start=1):
            fn = doc.metadata.get("filename", Path(doc.metadata.get("source", "Unknown")).name)
            pg = doc.metadata.get("page", 1)
            print(f"[{i}] {fn} (Page {pg})")
            snippet = doc.page_content.replace("\n", " ")[:140]
            print(f"    Excerpt: \"{snippet}...\"")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
