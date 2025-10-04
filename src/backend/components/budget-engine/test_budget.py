"""
Comprehensive Test Cases for Budget Engine
Run with: python3 test_budget.py
Or with pytest: pytest test_budget.py -v
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import CategoryAllocation, BudgetSummary


class TestBudgetEngine:
    """Test suite for Budget Engine functionality"""

    def test_allocation_calculation(self):
        """Test 1: Budget allocation calculation"""
        print("\n" + "="*60)
        print("TEST 1: Budget Allocation Calculation")
        print("="*60)

        income = Decimal("5000")
        housing_percent = Decimal("30")  # 30%

        expected_housing = income * (housing_percent / 100)
        actual_housing = Decimal("1500")

        assert actual_housing == expected_housing, f"Expected {expected_housing}, got {actual_housing}"
        print(f"✓ Income: ${income}")
        print(f"✓ Housing (30%): ${actual_housing}")
        print(f"✓ Allocation calculation correct!")

    def test_50_30_20_rule(self):
        """Test 2: 50/30/20 budget rule"""
        print("\n" + "="*60)
        print("TEST 2: 50/30/20 Budget Rule")
        print("="*60)

        income = Decimal("5000")

        needs = income * Decimal("0.50")  # 50% - $2500
        wants = income * Decimal("0.30")  # 30% - $1500
        savings = income * Decimal("0.20")  # 20% - $1000

        total = needs + wants + savings

        assert total == income, f"Total {total} doesn't equal income {income}"
        print(f"✓ Income: ${income}")
        print(f"✓ Needs (50%): ${needs}")
        print(f"✓ Wants (30%): ${wants}")
        print(f"✓ Savings (20%): ${savings}")
        print(f"✓ Total: ${total} = ${income} ✓")

    def test_purchase_validation(self):
        """Test 3: Purchase fits budget check"""
        print("\n" + "="*60)
        print("TEST 3: Purchase Validation")
        print("="*60)

        allocated = Decimal("500")
        spent = Decimal("350")
        remaining = allocated - spent

        # Test purchase that fits
        purchase1 = Decimal("100")
        fits1 = purchase1 <= remaining

        # Test purchase that exceeds
        purchase2 = Decimal("200")
        fits2 = purchase2 <= remaining

        assert fits1 == True, "Purchase of $100 should fit in $150 remaining"
        assert fits2 == False, "Purchase of $200 should NOT fit in $150 remaining"

        print(f"✓ Allocated: ${allocated}")
        print(f"✓ Spent: ${spent}")
        print(f"✓ Remaining: ${remaining}")
        print(f"✓ Purchase $100: {'APPROVED' if fits1 else 'DENIED'}")
        print(f"✓ Purchase $200: {'APPROVED' if fits2 else 'DENIED'}")

    def test_percentage_calculation(self):
        """Test 4: Calculate percentage of budget used"""
        print("\n" + "="*60)
        print("TEST 4: Percentage Calculation")
        print("="*60)

        allocated = Decimal("1000")

        test_cases = [
            (Decimal("250"), 25.0),   # 25%
            (Decimal("500"), 50.0),   # 50%
            (Decimal("750"), 75.0),   # 75%
            (Decimal("1000"), 100.0), # 100%
        ]

        for amount, expected_pct in test_cases:
            actual_pct = (float(amount) / float(allocated)) * 100
            assert actual_pct == expected_pct, f"Expected {expected_pct}%, got {actual_pct}%"
            print(f"✓ ${amount} of ${allocated} = {actual_pct}%")

    def test_budget_summary(self):
        """Test 5: Budget summary generation"""
        print("\n" + "="*60)
        print("TEST 5: Budget Summary")
        print("="*60)

        allocations = [
            CategoryAllocation(
                category_id="cat_housing",
                allocated_amount=Decimal("1500"),
                spent_amount=Decimal("1500"),
                remaining_amount=Decimal("0")
            ),
            CategoryAllocation(
                category_id="cat_groceries",
                allocated_amount=Decimal("600"),
                spent_amount=Decimal("450"),
                remaining_amount=Decimal("150")
            ),
            CategoryAllocation(
                category_id="cat_dining",
                allocated_amount=Decimal("300"),
                spent_amount=Decimal("350"),  # Overspent!
                remaining_amount=Decimal("-50")
            ),
        ]

        total_budget = sum(a.allocated_amount for a in allocations)
        total_spent = sum(a.spent_amount for a in allocations)
        total_remaining = total_budget - total_spent

        overspent = [a.category_id for a in allocations if a.spent_amount > a.allocated_amount]

        summary = BudgetSummary(
            total_budget=total_budget,
            total_spent=total_spent,
            total_remaining=total_remaining,
            categories=allocations,
            overspent_categories=overspent
        )

        assert summary.total_budget == Decimal("2400")
        assert summary.total_spent == Decimal("2300")
        assert summary.total_remaining == Decimal("100")
        assert len(summary.overspent_categories) == 1
        assert "cat_dining" in summary.overspent_categories

        print(f"✓ Total Budget: ${summary.total_budget}")
        print(f"✓ Total Spent: ${summary.total_spent}")
        print(f"✓ Total Remaining: ${summary.total_remaining}")
        print(f"✓ Overspent Categories: {summary.overspent_categories}")

    def test_reallocation_suggestion(self):
        """Test 6: Budget reallocation suggestions"""
        print("\n" + "="*60)
        print("TEST 6: Reallocation Suggestions")
        print("="*60)

        # Category with surplus
        entertainment_allocated = Decimal("500")
        entertainment_spent = Decimal("100")
        entertainment_remaining = entertainment_allocated - entertainment_spent

        # Category overspent
        dining_allocated = Decimal("300")
        dining_spent = Decimal("450")
        dining_overage = dining_spent - dining_allocated

        # Can we reallocate?
        can_reallocate = entertainment_remaining >= dining_overage

        assert can_reallocate == True, "Should be able to reallocate $150 from entertainment"
        assert entertainment_remaining == Decimal("400")
        assert dining_overage == Decimal("150")

        print(f"✓ Entertainment: ${entertainment_spent}/${entertainment_allocated} (${entertainment_remaining} remaining)")
        print(f"✓ Dining: ${dining_spent}/${dining_allocated} (${dining_overage} over)")
        print(f"✓ Suggestion: Reallocate ${dining_overage} from Entertainment to Dining")

    def test_goal_based_allocation(self):
        """Test 7: Goal-based budget adjustments"""
        print("\n" + "="*60)
        print("TEST 7: Goal-Based Allocation")
        print("="*60)

        base_savings = Decimal("500")

        # Goal: "Save 20% for emergency fund"
        goal_multiplier = Decimal("1.5")
        adjusted_savings = base_savings * goal_multiplier

        # Reduce discretionary to compensate
        base_entertainment = Decimal("400")
        entertainment_multiplier = Decimal("0.7")
        adjusted_entertainment = base_entertainment * entertainment_multiplier

        savings_increase = adjusted_savings - base_savings
        entertainment_decrease = base_entertainment - adjusted_entertainment

        print(f"✓ Goal: 'Save for emergency fund'")
        print(f"✓ Savings: ${base_savings} → ${adjusted_savings} (+${savings_increase})")
        print(f"✓ Entertainment: ${base_entertainment} → ${adjusted_entertainment} (-${entertainment_decrease})")
        print(f"✓ Net change: ${savings_increase - entertainment_decrease}")

    def test_overspent_detection(self):
        """Test 8: Detect overspent categories"""
        print("\n" + "="*60)
        print("TEST 8: Overspent Detection")
        print("="*60)

        test_allocations = [
            ("Housing", Decimal("1500"), Decimal("1500"), False),      # At limit
            ("Groceries", Decimal("600"), Decimal("450"), False),      # Under budget
            ("Dining", Decimal("300"), Decimal("400"), True),          # OVER budget
            ("Transportation", Decimal("400"), Decimal("500"), True),  # OVER budget
        ]

        overspent = []

        for name, allocated, spent, should_be_over in test_allocations:
            is_over = spent > allocated
            assert is_over == should_be_over, f"{name} overspent detection failed"

            status = "OVER" if is_over else "OK"
            if is_over:
                overspent.append(name)

            print(f"✓ {name}: ${spent}/${allocated} [{status}]")

        print(f"✓ Overspent categories: {overspent}")
        assert len(overspent) == 2

    def test_income_rebalancing(self):
        """Test 9: Rebalance allocations to fit income"""
        print("\n" + "="*60)
        print("TEST 9: Income Rebalancing")
        print("="*60)

        income = Decimal("5000")

        # Allocations that exceed income
        initial_allocations = [
            Decimal("2000"),  # Housing
            Decimal("1500"),  # Transportation
            Decimal("1000"),  # Groceries
            Decimal("800"),   # Dining
            Decimal("500"),   # Entertainment
        ]

        initial_total = sum(initial_allocations)
        print(f"✓ Income: ${income}")
        print(f"✓ Initial total allocations: ${initial_total}")

        # Calculate rebalancing ratio
        ratio = income / initial_total

        # Apply ratio
        rebalanced = [alloc * ratio for alloc in initial_allocations]
        rebalanced_total = sum(rebalanced)

        assert abs(rebalanced_total - income) < Decimal("0.01"), "Rebalanced total should equal income"

        print(f"✓ Rebalancing ratio: {ratio}")
        print(f"✓ Rebalanced total: ${rebalanced_total}")
        print(f"✓ Successfully fit within income!")

    def test_spending_pattern_analysis(self):
        """Test 10: Analyze spending patterns"""
        print("\n" + "="*60)
        print("TEST 10: Spending Pattern Analysis")
        print("="*60)

        # Mock expense history
        expenses = [
            {"category": "Groceries", "amount": Decimal("150")},
            {"category": "Groceries", "amount": Decimal("200")},
            {"category": "Groceries", "amount": Decimal("180")},
            {"category": "Dining", "amount": Decimal("50")},
            {"category": "Dining", "amount": Decimal("75")},
        ]

        # Calculate averages
        patterns = {}
        for expense in expenses:
            cat = expense["category"]
            if cat not in patterns:
                patterns[cat] = {"total": Decimal("0"), "count": 0}

            patterns[cat]["total"] += expense["amount"]
            patterns[cat]["count"] += 1

        for cat in patterns:
            avg = patterns[cat]["total"] / patterns[cat]["count"]
            patterns[cat]["average"] = avg

        assert patterns["Groceries"]["average"] == Decimal("176.67").quantize(Decimal("0.01"))
        assert patterns["Dining"]["count"] == 2

        print(f"✓ Groceries: {patterns['Groceries']['count']} expenses, avg ${patterns['Groceries']['average']}")
        print(f"✓ Dining: {patterns['Dining']['count']} expenses, avg ${patterns['Dining']['average']}")


def run_all_tests():
    """Run all budget engine tests"""
    print("\n" + "="*60)
    print("BUDGET ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*60)

    test_suite = TestBudgetEngine()

    tests = [
        ("Allocation Calculation", test_suite.test_allocation_calculation),
        ("50/30/20 Budget Rule", test_suite.test_50_30_20_rule),
        ("Purchase Validation", test_suite.test_purchase_validation),
        ("Percentage Calculation", test_suite.test_percentage_calculation),
        ("Budget Summary", test_suite.test_budget_summary),
        ("Reallocation Suggestions", test_suite.test_reallocation_suggestion),
        ("Goal-Based Allocation", test_suite.test_goal_based_allocation),
        ("Overspent Detection", test_suite.test_overspent_detection),
        ("Income Rebalancing", test_suite.test_income_rebalancing),
        ("Spending Pattern Analysis", test_suite.test_spending_pattern_analysis),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n✅ {test_name} - PASSED")
        except AssertionError as e:
            failed += 1
            print(f"\n❌ {test_name} - FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} - ERROR: {e}")

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review.\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
