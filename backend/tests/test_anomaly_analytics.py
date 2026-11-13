from analytics.anomaly_detector import detect
from analytics.insights import generate_insights


def test_duplicate_and_large_transaction_flags():
    rows = [
        {"date": "2025-01-01", "debit": 50, "credit": 0, "description": "UPI CAFE"},
        {"date": "2025-01-01", "debit": 50, "credit": 0, "description": "UPI CAFE"},
        {"date": "2025-01-03", "debit": 1000, "credit": 0, "description": "LARGE BILL"},
        {"date": "2025-01-04", "debit": 51, "credit": 0, "description": "FOOD"},
        {"date": "2025-02-01", "debit": 0, "credit": 1000, "description": "SALARY CREDIT"},
        {"date": "2025-02-01", "debit": 0, "credit": 1000, "description": "SALARY CREDIT"},
    ]
    flags = detect(rows)
    assert any("duplicate" in x["reason"].lower() for x in flags)
    assert any(x["method"] == "IQR" for x in flags)


def test_historical_duplicates_and_frequency_are_flagged():
    historical = [{"date": "2025-01-01", "debit": 75, "credit": 0, "description": "UPI COFFEE", "reference": "REF12345"}]
    current = [{"date": "2025-01-01", "debit": 75, "credit": 0, "description": "UPI COFFEE", "reference": "REF12345"}]
    assert any(flag["method"] == "cross_statement_duplicate" for flag in detect(current, historical))
    frequent = [{"date": f"2025-02-{i+1:02d}", "debit": 10, "credit": 0, "description": "REPEATED MERCHANT"} for i in range(5)]
    assert any(flag["method"] == "transaction_frequency" for flag in detect(frequent))


def test_insights_do_not_invent_empty_data():
    assert generate_insights([]) == {"available": False, "insights": []}


def test_insights_compare_months_and_detect_recurring_payment():
    rows = [
        {"date": "2025-01-05", "debit": 100, "credit": 0, "description": "MONTHLY INTERNET", "normalized_description": "monthly internet", "final_category": "Utilities"},
        {"date": "2025-02-05", "debit": 120, "credit": 0, "description": "MONTHLY INTERNET", "normalized_description": "monthly internet", "final_category": "Utilities"},
        {"date": "2025-02-10", "debit": 80, "credit": 0, "description": "FOOD ORDER", "normalized_description": "food order", "final_category": "Food & Dining"},
    ]
    result = generate_insights(rows)
    kinds = {item["type"] for item in result["insights"]}
    assert "month_over_month_spending" in kinds
    recurring = next(item for item in result["insights"] if item["type"] == "recurring_payments")
    assert recurring["count"] == 1
