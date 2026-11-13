from extraction.data_cleaner import parse_amount, normalize_date, clean_transaction, reconcile


def test_indian_amount_and_date_normalization():
    assert parse_amount("₹1,23,456.78 Dr") == 123456.78
    assert parse_amount("Rs. 1,23,456.78 Cr") == 123456.78
    assert parse_amount("INR 1,23,456.78") == 123456.78
    assert normalize_date("05/11/2025") == "2025-11-05"
    assert normalize_date("05-Nov-2025") == "2025-11-05"


def test_clean_preserves_original_description_and_warns_on_date():
    row = clean_transaction({"date": "bad", "description": "  UPI   SWIGGY  ", "debit": "(1,250.00)"})
    assert row["original_description"] == "  UPI   SWIGGY  "
    assert row["normalized_description"] == "upi swiggy"
    assert row["debit"] == -1250
    assert row["validation_warnings"]


def test_reconciliation_does_not_adjust_amounts():
    result = reconcile(100, [{"credit": 20, "debit": 5}], 115, .01)
    assert result["reconciled"] is True
