from datetime import datetime, timezone
from bson import ObjectId

VALID_STATUSES = {"uploaded", "processing", "completed", "failed"}


def validate_statement(document):
    if not isinstance(document.get("owner_id"), ObjectId): raise ValueError("statement.owner_id must be an ObjectId")
    if not document.get("filename") or not document.get("path"): raise ValueError("statement filename and storage path are required")
    if document.get("status") not in VALID_STATUSES: raise ValueError("invalid statement status")
    return document


def validate_transaction(document):
    if not isinstance(document.get("owner_id"), ObjectId) or not isinstance(document.get("statement_id"), ObjectId):
        raise ValueError("transaction owner_id and statement_id must be ObjectId references")
    if not isinstance(document.get("description"), str): raise ValueError("transaction description must be text")
    if document.get("date") is not None and not isinstance(document.get("date"), str): raise ValueError("transaction date must be normalized text or null")
    for field in ("debit", "credit", "balance", "confidence"):
        if document.get(field) is not None and not isinstance(document.get(field), (int, float)):
            raise ValueError(f"transaction {field} must be numeric or null")
    if not isinstance(document.get("final_category"), str): raise ValueError("transaction final_category is required")
    return document


def now():
    return datetime.now(timezone.utc)


def statement_document(owner_id, filename, path, metadata=None, file_sha256=None):
    return validate_statement({
        "owner_id": owner_id, "filename": filename, "path": path, "status": "uploaded", "metadata": metadata or {},
        "file_sha256": file_sha256, "duplicate_count": 0,
        "validation": {"warnings": [], "errors": [], "reconciled": None}, "created_at": now(), "updated_at": now()
    })


def transaction_document(owner_id, statement_id, row):
    return validate_transaction({"owner_id": owner_id, "statement_id": statement_id, **row, "created_at": now(), "updated_at": now()})
