"""Stable transaction fingerprints and owner-scoped duplicate cleanup."""
import hashlib
import json
import re


def transaction_fingerprint(transaction):
    date = str(transaction.get("date") or "").strip()
    description = transaction.get("normalized_description") or transaction.get("description") or ""
    description = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", str(description).lower())).strip()
    reference = re.sub(r"\s+", "", str(transaction.get("reference") or "").lower())
    balance = transaction.get("balance")
    # Without a reference or resulting balance, identical same-day charges can
    # be legitimate repeats. In that case rely on whole-file de-duplication.
    if not date or not description or (not reference and balance is None):
        return None
    def amount(value):
        return None if value is None else f"{float(value):.2f}"
    payload = [date, description, reference, amount(transaction.get("debit")),
               amount(transaction.get("credit")), amount(balance)]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode("utf-8")).hexdigest()


def deduplicate_owner_transactions(database, owner_id):
    """Keep the earliest exact financial row and remove its duplicate copies."""
    seen = set()
    statement_counts = {}
    removed_by_statement = {}
    removed = 0
    docs = database.transactions.find({"owner_id": owner_id}).sort([("created_at", 1), ("_id", 1)])
    for transaction in docs:
        # Recompute from the current transaction values so an edited date,
        # description, or amount cannot retain a stale duplicate identity.
        fingerprint = transaction_fingerprint(transaction)
        if not fingerprint:
            statement_id = transaction.get("statement_id")
            statement_counts[statement_id] = statement_counts.get(statement_id, 0) + 1
            continue
        if fingerprint in seen:
            tx_id = transaction["_id"]
            statement_id = transaction.get("statement_id")
            database.transactions.delete_one({"_id": tx_id, "owner_id": owner_id})
            database.anomaly_records.delete_many({"owner_id": owner_id, "transaction_id": {"$in": [str(tx_id), tx_id]}})
            database.model_feedback.delete_many({"owner_id": owner_id, "transaction_id": tx_id})
            removed_by_statement[statement_id] = removed_by_statement.get(statement_id, 0) + 1
            removed += 1
            continue
        seen.add(fingerprint)
        statement_id = transaction.get("statement_id")
        statement_counts[statement_id] = statement_counts.get(statement_id, 0) + 1
        if transaction.get("fingerprint") != fingerprint:
            database.transactions.update_one({"_id": transaction["_id"]}, {"$set": {"fingerprint": fingerprint}})
    for statement in database.bank_statements.find({"owner_id": owner_id}, {"_id": 1, "duplicate_count": 1}):
        count = statement_counts.get(statement["_id"], 0)
        increments = removed_by_statement.get(statement["_id"], 0)
        database.bank_statements.update_one(
            {"_id": statement["_id"], "owner_id": owner_id},
            {"$set": {"transaction_count": count}, **({"$inc": {"duplicate_count": increments}} if increments else {})},
        )
    return {"removed_count": removed, "fingerprints": seen}
