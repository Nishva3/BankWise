from exports.csv_export import make_csv
from exports.excel_export import make_excel


def test_exports_have_content():
    tx = [{"date": "2025-01-01", "description": "Salary", "credit": 100, "debit": 0, "final_category": "Salary & Income", "method": "rule", "confidence": 1}]
    assert "description" in make_csv(tx)
    assert make_excel(tx)[:2] == b"PK"


def test_empty_exports_still_include_expected_columns():
    csv_data = make_csv([])
    assert "date,description,debit,credit,balance" in csv_data
    excel = make_excel([])
    assert excel[:2] == b"PK"
