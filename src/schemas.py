from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="User question")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of context chunks to retrieve")
    user_role: str = Field(default="employee", description="Role for metadata RBAC filtering")

class SourceCitation(BaseModel):
    filename: str
    page: Optional[int] = None
    snippet: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    confidence_score: Optional[float] = None
