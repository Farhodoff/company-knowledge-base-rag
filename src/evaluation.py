from typing import List, Dict, Any

def compute_groundedness_ratio(answer: str, context_chunks: List[str]) -> float:
    """Estimate word overlap ratio between answer and context chunks."""
    if not answer or not context_chunks:
        return 0.0
    
    answer_words = set(answer.lower().split())
    context_words = set(" ".join(context_chunks).lower().split())
    
    if not answer_words:
        return 0.0
        
    overlap = answer_words.intersection(context_words)
    return round(len(overlap) / len(answer_words), 4)
