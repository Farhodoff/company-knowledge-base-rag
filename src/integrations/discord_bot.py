"""
Discord Integration Bot — Connects Discord channels to Company Knowledge Base RAG.
Answers questions using formatted Discord Embeds with verified document citations.

Environment Variables:
    DISCORD_BOT_TOKEN=...
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


def start_discord_bot():
    """Start Discord bot client."""
    try:
        import discord
        from discord.ext import commands
    except ImportError:
        print("❌ discord.py is not installed. Install it with: pip install discord.py")
        sys.exit(1)

    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN missing in .env")
        sys.exit(1)

    print("🚀 Initializing Discord Knowledge Base Bot...")
    rag = get_rag_runner()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Discord Bot logged in as {bot.user} (ID: {bot.user.id})")
        print("💡 Use '!ask <question>' in any text channel.")

    @bot.command(name="ask")
    async def ask_command(ctx, *, question: str):
        async with ctx.typing():
            try:
                answer, sources = rag(question)

                embed = discord.Embed(
                    title="🏢 Company Knowledge Base",
                    description=answer[:4000],
                    color=0x38BDF8,  # Sky blue
                )
                embed.add_field(name="❓ Question", value=question[:1024], inline=False)

                if sources:
                    source_lines = []
                    for doc in sources[:3]:
                        fn = doc.metadata.get("filename", Path(doc.metadata.get("source", "Doc")).name)
                        page = doc.metadata.get("page", 1)
                        source_lines.append(f"• **{fn}** (Page {page})")
                    embed.add_field(
                        name="📎 Verified Sources",
                        value="\n".join(source_lines),
                        inline=False,
                    )

                embed.set_footer(text="Grounded strictly in company documents • Powered by Gemini & FAISS")
                await ctx.reply(embed=embed)
            except Exception as e:
                await ctx.reply(f"⚠️ Error querying knowledge base: {e}")

    bot.run(token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discord Knowledge Base Bot")
    parser.add_argument("--test", type=str, help="Test query directly.")
    args = parser.parse_args()

    if args.test:
        rag = get_rag_runner()
        ans, src = rag(args.test)
        print("Answer:\n", ans)
        print("Sources:", [s.metadata.get("filename") for s in src])
    else:
        start_discord_bot()
