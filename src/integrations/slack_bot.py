"""
Slack Integration Bot — Answers employee questions directly in Slack channels or DMs.
Supports Slack Socket Mode (no public URL required) and Block Kit formatting.

Environment Variables:
    SLACK_BOT_TOKEN=xoxb-...
    SLACK_APP_TOKEN=xapp-...
"""

import os
import sys
import argparse
from pathlib import Path

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


def get_rag_runner():
    """Initialize and return RAG query function."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
    if not vectorstore_exists(VECTORSTORE_DIR):
        raise FileNotFoundError(f"Vector store not found at {VECTORSTORE_DIR}. Run ingest.py first.")

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
    return create_rag_chain_with_sources(llm, retriever)


def format_slack_blocks(question: str, answer: str, sources: list) -> list:
    """Format RAG response into Slack Block Kit structure."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Question:* {question}\n\n*Answer:*\n{answer}",
            },
        },
    ]

    if sources:
        source_texts = []
        for doc in sources[:3]:
            fn = doc.metadata.get("filename", Path(doc.metadata.get("source", "Doc")).name)
            page = doc.metadata.get("page", 1)
            source_texts.append(f"• `{fn}` (p.{page})")

        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📎 *Verified Sources:* " + " | ".join(source_texts),
                    }
                ],
            },
        ])

    return blocks


def start_slack_bot():
    """Start Slack Bolt app in Socket Mode."""
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError:
        print("❌ slack_bolt is not installed. Install it with: pip install slack_bolt")
        sys.exit(1)

    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")

    if not bot_token or not app_token:
        print("❌ SLACK_BOT_TOKEN or SLACK_APP_TOKEN missing in .env")
        print("Provide both tokens to start the Slack Socket Mode bot.")
        sys.exit(1)

    print("🚀 Initializing Slack Knowledge Base Bot...")
    rag = get_rag_runner()
    app = App(token=bot_token)

    @app.event("app_mention")
    def handle_mention(event, say):
        text = event.get("text", "")
        # Remove bot mention prefix <@U...>
        import re
        clean_prompt = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
        if not clean_prompt:
            say("Hello! Ask me any question about company policies, onboarding, or coding standards.")
            return

        thread_ts = event.get("thread_ts") or event.get("ts")
        say(text="Searching company documents...", thread_ts=thread_ts)

        try:
            answer, sources = rag(clean_prompt)
            blocks = format_slack_blocks(clean_prompt, answer, sources)
            say(blocks=blocks, text=answer, thread_ts=thread_ts)
        except Exception as e:
            say(text=f"⚠️ Error querying knowledge base: {e}", thread_ts=thread_ts)

    print("✅ Slack Bot listening for @mentions via Socket Mode...")
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack Knowledge Base Bot")
    parser.add_argument("--test", type=str, help="Run a test query without launching Slack listener.")
    args = parser.parse_args()

    if args.test:
        rag = get_rag_runner()
        ans, src = rag(args.test)
        print("Formatted Slack Blocks:")
        import json
        print(json.dumps(format_slack_blocks(args.test, ans, src), indent=2))
    else:
        start_slack_bot()
