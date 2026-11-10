from typing import Dict, Any, List
from langchain_core.documents import Document

def filter_documents_by_role(docs: List[Document], user_role: str) -> List[Document]:
    """Filter retrieved documents based on user access role."""
    if user_role == "admin":
        return docs
    
    allowed = []
    for doc in docs:
        roles = doc.metadata.get("roles", ["all"])
        if "all" in roles or user_role in roles:
            allowed.append(doc)
    return allowed
