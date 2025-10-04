import re
from typing import Optional
from decimal import Decimal

def normalize_merchant(raw_merchant: str) -> str:
    """
    Normalize merchant names for consistent matching.
    Removes punctuation, numbers, and converts to lowercase.
    Example: "Trader Joe's #122" → "trader joes"
    """
    # Convert to lowercase
    normalized = raw_merchant.lower()

    # Remove common suffixes and numbers
    normalized = re.sub(r'#\d+', '', normalized)  # Remove #123
    normalized = re.sub(r'\d+', '', normalized)   # Remove numbers

    # Remove punctuation except spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)

    # Remove extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized.strip()

def extract_amount_from_text(text: str) -> Optional[Decimal]:
    """Extract monetary amount from text"""
    # Match patterns like $123.45, 123.45, $123
    patterns = [
        r'\$\s*(\d+(?:\.\d{2})?)',  # $123.45 or $123
        r'(\d+\.\d{2})',             # 123.45
        r'(\d+)\s*(?:dollars|bucks)', # 123 dollars
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return Decimal(match.group(1))
            except:
                pass

    return None

def calculate_confidence_from_scores(scores: list[float]) -> float:
    """
    Calculate confidence based on difference between top two scores.
    Higher difference = higher confidence
    """
    if not scores or len(scores) == 0:
        return 0.0

    if len(scores) == 1:
        return scores[0]

    sorted_scores = sorted(scores, reverse=True)
    top = sorted_scores[0]
    second = sorted_scores[1] if len(sorted_scores) > 1 else 0.0

    if top == 0:
        return 0.0

    # Confidence is based on the gap between top and second
    # Larger gap = more confident
    confidence = top * (1 - (second / top)) if top > 0 else 0.0

    return min(confidence, 1.0)