import fitz
import pytest
from pathlib import Path

from extraction.bank_parser import identify_bank, parse_pages
from extraction.pdf_detector import inspect_pdf
from extraction.text_extractor import extract_text


SAMPLES = {
    "SBI": "State Bank of India\nAccount Number: 123456789012\nAccount Holder: Asha Sharma\nOpening Balance: ₹1,000.00\nClosing Balance: ₹550.00\nTxn Date    Value Date    Description    Debit    Credit    Balance\n01/04/2025    01/04/2025    UPI/DR/SWIGGY    ₹450.00    0.00    ₹550.00",
    "HDFC": "HDFC Bank Statement\nAccount No: 123456789012\nOpening Balance: ₹1,000.00\nClosing Balance: ₹550.00\nDate    Narration    Chq./Ref.No.    ValueDt    WithdrawalAmt.    DepositAmt.    ClosingBalance\n01/04/2025    UPI-DEBIT-SWIGGY    UTR12345    01/04/2025    ₹450.00    0.00    ₹550.00",
    "ICICI": "ICICI Bank Statement\nAccount Holder: Asha Sharma\nIFSC: ICIC0001234\nOpening Balance: ₹1,000.00\nClosing Balance: ₹1,450.00\nTransaction Date    Particulars    Transaction ID    Debit    Credit    Balance\n01/04/2025    NEFT SALARY CREDIT    NEFT12345    0.00    ₹450.00    ₹1,450.00",
    "Axis": "Axis Bank Statement\nAccount Holder: Asha Sharma\nIFSC: UTIB0001234\nOpening Balance: ₹1,000.00\nClosing Balance: ₹650.00\nTran Date    Particulars    Reference No    Value Date    Dr Amount    Cr Amount    Balance\n01/04/2025    UPI ZOMATO ORDER    UPI12345    01/04/2025    ₹350.00    0.00    ₹650.00",
}


@pytest.mark.parametrize("bank,text", SAMPLES.items())
def test_synthetic_bank_pdf_layouts(bank, text, tmp_path):
    # Synthetic parser fixtures exercise known layout variants; these are not bank-issued statements.
    path = tmp_path / f"{bank.lower()}-synthetic.pdf"
    doc = fitz.open(); page = doc.new_page()
    page.insert_text((48, 60), text, fontsize=11)
    doc.save(path); doc.close()
    assert inspect_pdf(path)["type"] == "text"
    parsed = parse_pages(extract_text(path))
    assert parsed["bank_name"] == bank
    assert len(parsed["transactions"]) == 1
    assert parsed["transactions"][0]["date"] == "01/04/2025"
    assert parsed["transactions"][0]["balance"] is not None


def test_identifies_unknown_and_parses_generic():
    assert identify_bank("A completely unknown bank") == "Unknown"
    parsed = parse_pages(["01/04/2025 UPI SWIGGY 450.00 Dr 1000.00"])
    assert parsed["transactions"][0]["description"] == "UPI SWIGGY"
    assert parsed["transactions"][0]["debit"] == 450


def test_bank_name_in_transaction_narration_does_not_override_statement_header():
    parsed = parse_pages(["ICICI Bank Statement\nAccount Holder: Asha Sharma\n01/04/2025 TRANSFER TO HDFC BANK 100.00 Dr 900.00"])
    assert parsed["bank_name"] == "ICICI"


def test_header_mapped_columns_value_date_and_rupee_balances():
    header = "Transaction Date    Narration    Value Date    Withdrawal Amount    Deposit Amount    Closing Balance"
    row = "01-04-2025    UPI/DR/SWIGGY    01-04-2025    ₹450.00    0.00    ₹550.00"
    parsed = parse_pages(["HDFC Bank Statement\nOpening Balance: ₹1,000.00\nClosing Balance: ₹550.00", header, row])
    assert parsed["opening_balance"] == 1000
    assert parsed["closing_balance"] == 550
    tx = parsed["transactions"][0]
    assert tx["date"] == "01-04-2025"
    assert tx["value_date"] == "01-04-2025"
    assert tx["debit"] == 450 and tx["credit"] == 0 and tx["balance"] == 550


def test_multpage_continuation_and_repeated_header_rows():
    header = "Transaction Date    Narration    Debit    Credit    Balance"
    parsed = parse_pages([
        "HDFC Bank Statement\n" + header + "\n01/04/2025    UPI SWIGGY    100.00    0.00    900.00",
        header + "\n02/04/2025    UPI ZOMATO    200.00    0.00    700.00",
    ])
    assert len(parsed["transactions"]) == 2
    assert parsed["transactions"][0]["description"] == "UPI SWIGGY"
    assert parsed["transactions"][1]["description"] == "UPI ZOMATO"


def test_corrupt_pdf_is_rejected(tmp_path):
    path = tmp_path / "broken.pdf"; path.write_bytes(b"not a pdf")
    with pytest.raises(ValueError, match="readable PDF"):
        inspect_pdf(path)


def test_distributed_sample_statements_extract_and_reconcile():
    from extraction.data_cleaner import clean_transaction, reconcile
    sample_dir = Path(__file__).resolve().parents[2] / "dataset" / "statements"
    for bank in ("sbi", "hdfc", "icici", "axis"):
        path = sample_dir / f"{bank}_synthetic_sample.pdf"
        parsed = parse_pages(extract_text(path))
        rows = [clean_transaction(row) for row in parsed["transactions"]]
        assert len(rows) == 4, path.name
        assert parsed["bank_name"].lower() == bank
        assert parsed["account_holder"] == "TEST USER"
        assert parsed["account_number"] == "XXXXXX1234"
        assert parsed["ifsc"] is not None
        assert parsed["statement_period"] is not None
        assert reconcile(parsed["opening_balance"], rows, parsed["closing_balance"])["reconciled"] is True
