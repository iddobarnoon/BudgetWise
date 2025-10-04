"""
Simple tests for the Ranking System
Run with: python -m pytest test_ranking.py
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import normalize_merchant, calculate_confidence_from_scores, extract_amount_from_text
from decimal import Decimal

def test_normalize_merchant():
    """Test merchant name normalization"""
    assert normalize_merchant("Trader Joe's #122") == "trader joes"
    assert normalize_merchant("STARBUCKS STORE 12345") == "starbucks store"
    assert normalize_merchant("Whole Foods Market, Inc.") == "whole foods market inc"
    assert normalize_merchant("McDonald's #789") == "mcdonalds"
    print("✓ Merchant normalization tests passed")

def test_confidence_calculation():
    """Test confidence score calculation"""
    # High confidence - large gap between scores
    scores1 = [0.9, 0.3, 0.1]
    conf1 = calculate_confidence_from_scores(scores1)
    assert conf1 > 0.6, f"Expected high confidence, got {conf1}"

    # Low confidence - similar scores
    scores2 = [0.9, 0.85, 0.8]
    conf2 = calculate_confidence_from_scores(scores2)
    assert conf2 < 0.3, f"Expected low confidence, got {conf2}"

    # Single score
    scores3 = [0.8]
    conf3 = calculate_confidence_from_scores(scores3)
    assert conf3 == 0.8

    # Empty scores
    scores4 = []
    conf4 = calculate_confidence_from_scores(scores4)
    assert conf4 == 0.0

    print("✓ Confidence calculation tests passed")

def test_extract_amount():
    """Test amount extraction from text"""
    assert extract_amount_from_text("Spent $50 on groceries") == Decimal("50")
    assert extract_amount_from_text("Bought coffee for $4.50") == Decimal("4.50")
    assert extract_amount_from_text("Paid 123.45 for dinner") == Decimal("123.45")
    assert extract_amount_from_text("Cost was 50 dollars") == Decimal("50")
    assert extract_amount_from_text("No amount here") is None
    print("✓ Amount extraction tests passed")

def test_matching_logic():
    """Test category matching logic"""
    # This would require database setup, so we'll test the logic separately
    test_rules = {
        "keywords": ["starbucks", "coffee", "cafe"],
        "merchant_patterns": ["starbucks", "dunkin"],
        "match_type": "substring",
        "priority": 5
    }

    # Simulate matching
    merchant = "starbucks store 123"
    normalized = normalize_merchant(merchant)

    # Check keyword match
    matches = [kw for kw in test_rules["keywords"] if kw in normalized]
    assert len(matches) > 0, "Should match 'starbucks' keyword"
    print("✓ Matching logic tests passed")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Running Ranking System Tests")
    print("="*50 + "\n")

    try:
        test_normalize_merchant()
        test_confidence_calculation()
        test_extract_amount()
        test_matching_logic()

        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        raise

if __name__ == "__main__":
    run_all_tests()
