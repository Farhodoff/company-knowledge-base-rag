"""
RAG Chain — Retrieval-Augmented Generation pipeline.
Retrieves context, then generates answer using LLM.
"""

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


# System prompt for answer generation
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful internal assistant for company employees. Answer questions
based ONLY on the provided context. If the answer is not in the context, say "I don't have
that information in the company documents." Do not invent information. When relevant, cite
the source document.

Context:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)


def create_rag_chain(llm, retriever):
    """
    Create a RAG chain: question → retrieve → format → generate.

    Returns a runnable that takes {"question": str} and outputs the answer string.
    """
    def format_docs(docs: List[Document]) -> str:
        return "\n\n---\n\n".join(
            f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            for doc in docs
        )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


def create_rag_chain_with_sources(llm, retriever):
    """
    Create a RAG chain that also returns source documents for citation.
    Returns (answer, sources).
    """
    def format_docs(docs: List[Document]) -> str:
        return "\n\n---\n\n".join(
            f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            for doc in docs
        )

    def retrieve_and_format(question: str):
        docs = retriever.invoke(question)
        return format_docs(docs), docs

    def generate(question_and_context):
        question = question_and_context["question"]
        context_str, sources = retrieve_and_format(question)
        prompt = RAG_PROMPT.format_messages(context=context_str, question=question)
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        return answer, sources

    def run(question: str):
        result = generate({"question": question})
        return result

    return run
