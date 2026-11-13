from bson import ObjectId
import pytest

from database.schemas import statement_document, transaction_document


def test_document_factories_validate_objectid_references_and_fields():
    owner_id, statement_id = ObjectId(), ObjectId()
    statement = statement_document(owner_id, "sample.pdf", "uploads/random.pdf")
    tx = transaction_document(owner_id, statement_id, {"description": "UPI CAFE", "date": "2025-01-01", "debit": 20.0, "credit": 0.0, "balance": 80.0, "final_category": "Food & Dining"})
    assert statement["status"] == "uploaded"
    assert tx["owner_id"] == owner_id and tx["statement_id"] == statement_id


def test_transaction_schema_rejects_invalid_amount_type():
    with pytest.raises(ValueError, match="debit must be numeric"):
        transaction_document(ObjectId(), ObjectId(), {"description": "x", "date": None, "debit": "many", "credit": 0, "final_category": "Other"})
