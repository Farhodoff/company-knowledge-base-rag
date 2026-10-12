"""
Company Knowledge Base RAG Chatbot — Enterprise Streamlit Interface.
Run: streamlit run app.py
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st

# Setup project path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DOCUMENTS_DIR,
    VECTORSTORE_DIR,
    MANIFEST_FILE,
    TOP_K_RETRIEVAL,
    SEARCH_TYPE,
    GOOGLE_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    TEMPERATURE,
)
from src.vectorstore import load_vectorstore, vectorstore_exists, create_vectorstore
from src.retriever import get_retriever
from src.chain import create_rag_chain_with_sources
from src.document_loader import load_documents_from_directory, SUPPORTED_EXTENSIONS
from src.chunker import chunk_documents
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Page Setup
st.set_page_config(
    page_title="Company Knowledge Base | AI Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .source-badge {
        display: inline-block;
        background: #0284c7;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .status-card {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #1e293b;
        margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_manifest_stats() -> Dict[str, Any]:
    """Read index manifest if available."""
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


@st.cache_resource(show_spinner=False)
def load_rag_pipeline(model_name: str, temp: float, top_k: int, search_mode: str):
    """Load vector store and RAG pipeline with caching."""
    if not GOOGLE_API_KEY:
        return None, "GOOGLE_API_KEY not found. Please set it in .env or environment variables."

    if not vectorstore_exists(VECTORSTORE_DIR):
        return None, "Vector index not found. Ingest documents first using the sidebar or CLI."

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
            transport="rest",
            request_timeout=90,
        )
        vectorstore = load_vectorstore(VECTORSTORE_DIR, embeddings)
        retriever = get_retriever(vectorstore, top_k=top_k, search_type=search_mode)

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=temp,
            request_timeout=90,
        )

        rag_with_sources = create_rag_chain_with_sources(llm, retriever)
        return rag_with_sources, None
    except Exception as e:
        return None, f"Failed to initialize RAG pipeline: {str(e)}"


def run_ingestion_in_ui() -> bool:
    """Run document loading, chunking, and embedding from UI."""
    if not GOOGLE_API_KEY:
        st.sidebar.error("Set GOOGLE_API_KEY before running ingestion.")
        return False

    with st.spinner("Indexing documents into FAISS vector store..."):
        try:
            docs = load_documents_from_directory(DOCUMENTS_DIR)
            if not docs:
                st.sidebar.warning(f"No files in {DOCUMENTS_DIR.name}/ to index.")
                return False

            chunks = chunk_documents(docs)
            embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                google_api_key=GOOGLE_API_KEY,
                transport="rest",
            )
            create_vectorstore(chunks, embeddings, VECTORSTORE_DIR)
            st.cache_resource.clear()
            st.sidebar.success(f"Indexed {len(chunks)} chunks across {len(docs)} files!")
            return True
        except Exception as e:
            st.sidebar.error(f"Ingestion failed: {e}")
            return False


# Localization dictionary
I18N = {
    "uz": {
        "page_title": "Kompaniya Bilimlar Bazasi | AI Yordamchi",
        "control_center": "⚙️ Boshqaruv Markazi",
        "language_select": "🌐 Tilni tanlang / Language",
        "index_status": "📊 Indeks holati",
        "index_active": "✅ FAISS vektor indeksi faol",
        "no_index": "⚠️ Vektor indeksi topilmadi",
        "chunks": "Fragmentlar",
        "sources": "Manbalar",
        "updated": "Yangilangan",
        "add_docs": "📥 Yangi Hujjat Qo‘shish",
        "upload_label": "Kompaniya qoidalari yoki qo‘llanmalarini yuklang",
        "saved_msg": "ta fayl `documents/` papkasiga saqlandi.",
        "reindex_btn": "🔄 Bilimlar Bazasini Qayta Indekslash",
        "available_docs": "📁 Mavjud Hujjatlar",
        "model_settings": "🎛️ Model va Qidiruv Sozlamalari",
        "llm_model": "LLM Modeli",
        "temp": "Kreativlik (Temperature)",
        "top_k": "Qidiriladigan qismlar (Top-K)",
        "search_algo": "Qidiruv algoritmi",
        "clear_chat": "🧹 Chatni tozalash",
        "main_title": "🏢 Kompaniya Bilimlar Bazasi AI",
        "sub_title": "Kompaniya reglamentlari, texnik standartlari va qo‘llanmalari asosida aniq va to‘g‘ri javob beruvchi ichki AI yordamchi.",
        "q_vacation": "🌴 Ta’til siyosati",
        "q_backend": "💻 Backend standartlari",
        "q_onboard": "🚀 Onboarding jarayoni",
        "q_security": "🔐 IT Xavfsizlik qoidalari",
        "prompt_vacation": "Xodimlar yiliga necha kun pullik ta’til (PTO) oladi va ta’tilga ariza qanday topshiriladi?",
        "prompt_backend": "Git branchlar, commitlar va PR ko‘rib chiqish bo‘yicha texnik talablar qanday?",
        "prompt_onboard": "Yangi xodim birinchi 3 kunlik onboarding davrida nimalarni bajarishi kerak?",
        "prompt_security": "2FA (Ikki bosqichli autentifikatsiya) va parollar xavfsizligi bo‘yicha majburiy qoidalar nimalardan iborat?",
        "verified_sources": "📎 Tasdiqlangan Manbalar:",
        "input_placeholder": "Kompaniya qoidalari yoki texnik qo‘llanmalar bo‘yicha savolingizni yozing...",
        "searching": "Hujjatlar o‘rganilmoqda va asosli javob tayyorlanmoqda...",
        "page": "Sahifa",
    },
    "en": {
        "page_title": "Company Knowledge Base | AI Assistant",
        "control_center": "⚙️ Control Center",
        "language_select": "🌐 Language / Tilni tanlang",
        "index_status": "📊 Index Status",
        "index_active": "✅ FAISS Vector Index Active",
        "no_index": "⚠️ No Vector Index Found",
        "chunks": "Chunks",
        "sources": "Sources",
        "updated": "Updated",
        "add_docs": "📥 Add Documents",
        "upload_label": "Upload policy or guides",
        "saved_msg": "file(s) saved to `documents/`.",
        "reindex_btn": "🔄 Re-index Knowledge Base",
        "available_docs": "📁 Available Docs",
        "model_settings": "🎛️ Retrieval & Model Settings",
        "llm_model": "LLM Model",
        "temp": "Creativity (Temperature)",
        "top_k": "Top-K Chunks",
        "search_algo": "Search Algorithm",
        "clear_chat": "🧹 Clear Conversation",
        "main_title": "🏢 Company Knowledge Base AI",
        "sub_title": "Internal AI assistant answering employee questions strictly grounded in company handbooks, standards, and policies.",
        "q_vacation": "🌴 Vacation Policy",
        "q_backend": "💻 Backend Standards",
        "q_onboard": "🚀 Onboarding Process",
        "q_security": "🔐 IT Security Rules",
        "prompt_vacation": "How many annual vacation days do employees get, and how do I request time off?",
        "prompt_backend": "What are our engineering standards for git branches, commits, and API errors?",
        "prompt_onboard": "What steps should a new employee complete during their first week?",
        "prompt_security": "What are the rules regarding password security, 2FA, and device access?",
        "verified_sources": "📎 Verified Sources:",
        "input_placeholder": "Ask any question regarding company policies or engineering guidelines...",
        "searching": "Searching documents & generating grounded response...",
        "page": "Page",
    }
}


def main():
    # --- Sidebar ---
    # Language Selector at top of sidebar
    selected_lang_label = st.sidebar.selectbox(
        "🌐 Til / Language",
        options=["🇺🇿 O'zbekcha", "🇬🇧 English"],
        index=0,
    )
    lang_code = "uz" if "O'zbekcha" in selected_lang_label else "en"
    t = I18N[lang_code]

    st.sidebar.title(t["control_center"])

    # Status & Index Info
    has_index = vectorstore_exists(VECTORSTORE_DIR)
    manifest = get_manifest_stats()

    st.sidebar.markdown(f"### {t['index_status']}")
    if has_index:
        st.sidebar.success(t["index_active"])
        if manifest:
            st.sidebar.caption(
                f"• {t['chunks']}: **{manifest.get('total_chunks', 'N/A')}**\n"
                f"• {t['sources']}: **{manifest.get('unique_sources', 'N/A')} files**\n"
                f"• {t['updated']}: `{manifest.get('created_at', '')[:16].replace('T', ' ')}`"
            )
    else:
        st.sidebar.warning(t["no_index"])

    # Document Uploader in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {t['add_docs']}")
    uploaded_files = st.sidebar.file_uploader(
        t["upload_label"],
        type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uf in uploaded_files:
            target_path = DOCUMENTS_DIR / uf.name
            if not target_path.exists():
                with open(target_path, "wb") as f:
                    f.write(uf.getbuffer())
        st.sidebar.info(f"{len(uploaded_files)} {t['saved_msg']}")

    if st.sidebar.button(t["reindex_btn"], use_container_width=True):
        if run_ingestion_in_ui():
            st.rerun()

    # Document list preview
    existing_docs = [p.name for p in DOCUMENTS_DIR.glob("*") if p.is_file() and not p.name.startswith(".")]
    with st.sidebar.expander(f"{t['available_docs']} ({len(existing_docs)})"):
        for name in sorted(existing_docs):
            st.caption(f"• `{name}`")

    # Model & Retrieval Settings
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {t['model_settings']}")
    selected_model = st.sidebar.selectbox(
        t["llm_model"],
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
    )
    selected_temp = st.sidebar.slider(t["temp"], 0.0, 1.0, TEMPERATURE, 0.05)
    selected_top_k = st.sidebar.slider(t["top_k"], 1, 10, TOP_K_RETRIEVAL, 1)
    selected_search = st.sidebar.radio(t["search_algo"], ["similarity", "mmr"], horizontal=True)

    if st.sidebar.button(t["clear_chat"], use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # --- Main Chat UI ---
    st.markdown(f'<div class="main-title">{t["main_title"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-title">{t["sub_title"]}</div>',
        unsafe_allow_html=True,
    )

    # Sample Quick Questions
    col1, col2, col3, col4 = st.columns(4)
    quick_prompt = None
    if col1.button(t["q_vacation"], use_container_width=True):
        quick_prompt = t["prompt_vacation"]
    if col2.button(t["q_backend"], use_container_width=True):
        quick_prompt = t["prompt_backend"]
    if col3.button(t["q_onboard"], use_container_width=True):
        quick_prompt = t["prompt_onboard"]
    if col4.button(t["q_security"], use_container_width=True):
        quick_prompt = t["prompt_security"]

    # Chat history state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.markdown(f"**{t['verified_sources']}**")
                for s in msg["sources"]:
                    fn = s.metadata.get("filename") or Path(s.metadata.get("source", "Unknown")).name
                    page = s.metadata.get("page")
                    label = f"📄 `{fn}`" + (f" — {t['page']} {page}" if page else "")
                    with st.expander(label):
                        st.markdown(f"> *{s.page_content[:450]}...*")

    # Handle input prompt
    user_query = st.chat_input(t["input_placeholder"])
    prompt_to_run = quick_prompt or user_query

    if prompt_to_run:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            rag_pipeline, err = load_rag_pipeline(
                model_name=selected_model,
                temp=selected_temp,
                top_k=selected_top_k,
                search_mode=selected_search,
            )

            if err:
                st.error(err)
            else:
                with st.spinner(t["searching"]):
                    try:
                        # Append language guidance if user language is Uzbek
                        effective_prompt = prompt_to_run
                        if lang_code == "uz" and not any(w in prompt_to_run.lower() for w in ["in english", "english please"]):
                            effective_prompt = f"{prompt_to_run}\n(Iltimos, javobni o'zbek tilida, professional va aniq shaklda taqdim eting)."

                        answer, sources = rag_pipeline(effective_prompt)
                        st.markdown(answer)

                        if sources:
                            st.markdown("---")
                            st.markdown(f"**{t['verified_sources']}**")
                            for s in sources:
                                fn = s.metadata.get("filename") or Path(s.metadata.get("source", "Unknown")).name
                                page = s.metadata.get("page")
                                label = f"📄 `{fn}`" + (f" — {t['page']} {page}" if page else "")
                                with st.expander(label):
                                    st.markdown(f"> *{s.page_content[:450]}...*")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        })
                    except Exception as e:
                        st.error(f"Error executing query: {str(e)}")


if __name__ == "__main__":
    main()
