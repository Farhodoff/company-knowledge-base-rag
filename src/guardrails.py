from typing import Tuple, List
from langchain_core.documents import Document

FALLBACK_OUT_OF_DOMAIN_UZ = (
    "Kechirasiz, kompaniyamizning ichki me'yoriy hujjatlarida ushbu mavzu bo'yicha ma'lumot topilmadi. "
    "Iltimos, tegishli bo'lim yoki HR xizmatiga murojaat qiling."
)

FALLBACK_OUT_OF_DOMAIN_EN = (
    "I cannot find this information in the uploaded company documents. "
    "Please reach out to the relevant department or HR administrator."
)

def evaluate_retrieval_confidence(docs_with_scores: List[Tuple[Document, float]], max_allowed_distance: float = 0.75) -> bool:
    """Return True if at least one retrieved chunk satisfies distance threshold."""
    if not docs_with_scores:
        return False
    # In L2 / Cosine distance: smaller score = more similar
    best_score = min(score for _, score in docs_with_scores)
    return best_score <= max_allowed_distance
