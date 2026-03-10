"""
Company Knowledge Base RAG Chatbot — Streamlit Chat UI.
Run: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# Project root
project_root = Path(__file__).resolve().parent

# Load environment
from dotenv import load_dotenv

load_dotenv(project_root / ".env")

import sys

sys.path.insert(0, str(project_root))

from config import (
    VECTORSTORE_DIR,
    TOP_K_RETRIEVAL,
    GOOGLE_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.vectorstore import load_vectorstore
from src.retriever import get_retriever
from src.chain import create_rag_chain, create_rag_chain_with_sources


# Page config
st.set_page_config(
    page_title="Company Knowledge Base",
    page_icon="📚",
    layout="centered",
)

# Custom styles
st.markdown(
    """
    <style>
    .source-box {
        background-color: #f0f2f6;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .source-title {
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_rag():
    """Load vector store and RAG components (cached)."""
    if not GOOGLE_API_KEY:
        st.error("GOOGLE_API_KEY not set. Add it to .env")
        st.stop()

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        transport="rest",
        request_timeout=60,
    )

    index_path = VECTORSTORE_DIR / "index.faiss"
    if not index_path.exists():
        st.warning(
            "Vector store not found. Run ingestion first:\n\n"
            "```\npython scripts/ingest.py\n```\n\n"
            "Place documents in the `documents/` folder."
        )
        st.stop()

    vectorstore = load_vectorstore(VECTORSTORE_DIR, embeddings)
    retriever = get_retriever(vectorstore, top_k=TOP_K_RETRIEVAL)
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        transport="rest",
        request_timeout=60,
    )
    chain = create_rag_chain(llm, retriever)
    rag_with_sources = create_rag_chain_with_sources(llm, retriever)

    return rag_with_sources, retriever


def main():
    st.title("📚 Company Knowledge Base")
    st.caption("Ask questions about company documents (vacation policy, coding standards, onboarding, etc.)")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Load RAG
    rag_with_sources, _ = load_rag()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.markdown("**Sources:**")
                for s in msg["sources"]:
                    source_path = s.metadata.get("source", "Unknown")
                    page = s.metadata.get("page", "")
                    label = f"{Path(source_path).name}" + (f" (p.{page})" if page else "")
                    with st.expander(label):
                        st.text(s.page_content[:500] + ("..." if len(s.page_content) > 500 else ""))

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                try:
                    answer, sources = rag_with_sources(prompt)
                    st.markdown(answer)
                    sources = sources or []
                    if sources:
                        st.markdown("---")
                        st.markdown("**📎 Sources:**")
                        for doc in sources:
                            source_path = doc.metadata.get("source", "Unknown")
                            page = doc.metadata.get("page", "")
                            label = f"`{Path(source_path).name}`" + (f" (page {page})" if page else "")
                            with st.expander(label):
                                st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
                    sources = []


if __name__ == "__main__":
    main()
