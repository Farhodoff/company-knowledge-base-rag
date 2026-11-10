def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters in English/code, ~2 in Uzbek)."""
    if not text:
        return 0
    # Conservative baseline: 3 characters per token
    return max(1, len(text) // 3)

def check_context_window_limit(text: str, max_tokens: int = 8000) -> bool:
    return estimate_tokens(text) <= max_tokens
