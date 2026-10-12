"""
RAG Chain — Retrieval-Augmented Generation pipeline.
Grounds LLM answers strictly on retrieved document context with verifiable source citations.
"""

from typing import List, Tuple, Optional, Any
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

SYSTEM_TEMPLATE = """You are the internal AI Knowledge Assistant for company team members.
Your mission is to provide accurate, concise, and helpful answers strictly based on the provided company documents.

Core Rules:
1. Grounding: Answer ONLY using information from the context below. Do NOT assume or invent facts outside the text.
2. Missing Information: If the context does not contain enough information to answer the question, state:
   "I cannot find this information in the uploaded company documents."
3. Citation: When providing specific policies, numbers, steps, or rules, reference the source document filename (and page/section if available).
4. Tone: Professional, structured, and easy to read (use bullet points and bold text where appropriate).

Context Documents:
{context}
"""

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{question}"),
    ]
)


def format_docs(docs: List[Document]) -> str:
    """Format retrieved document chunks into clean markdown context blocks."""
    if not docs:
        return "No relevant documents found."

    formatted_blocks = []
    for doc in docs:
        filename = doc.metadata.get("filename") or Path(doc.metadata.get("source", "Unknown")).name
        page = doc.metadata.get("page")
        page_str = f" (Page {page})" if page else ""
        formatted_blocks.append(f"### [Source: {filename}{page_str}]\n{doc.page_content}")

    return "\n\n---\n\n".join(formatted_blocks)


def create_rag_chain(llm: Any, retriever: Any):
    """
    Build a standard LCEL chain: question → retriever → format → prompt → llm → parser.
    """
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "chat_history": lambda _: [],
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


def create_rag_chain_with_sources(llm: Any, retriever: Any):
    """
    Build a RAG pipeline that returns both the generated answer and the source Document chunks.
    Supports optional chat_history (list of tuples or BaseMessage).
    """
    def run(question: str, chat_history: Optional[List[Any]] = None) -> Tuple[str, List[Document]]:
        docs = retriever.invoke(question)
        context_str = format_docs(docs)

        history_msgs = chat_history or []
        prompt = RAG_PROMPT.format_messages(
            context=context_str,
            question=question,
            chat_history=history_msgs,
        )
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)

        return str(answer), docs

    return run
