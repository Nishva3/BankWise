from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .common import db, owner, oid, serialize, fail
from analytics.anomaly_detector import detect, contextualize_legacy_reason

bp = Blueprint("anomalies", __name__, url_prefix="/api/anomalies")


@bp.post("/scan")
@jwt_required()
def scan_transactions():
    """Run the configured anomaly heuristics over the signed-in user's ledger."""
    transactions = list(db().transactions.find({"owner_id": owner()}))
    flags = detect(transactions)
    expected = {(flag["transaction_id"], flag["reason"]): flag for flag in flags}
    created = 0
    stale = 0
    for current in db().anomaly_records.find({"owner_id": owner(), "review_status": "pending"}):
        key = (current.get("transaction_id"), current.get("reason"))
        if key not in expected:
            db().anomaly_records.delete_one({"_id": current["_id"], "owner_id": owner()})
            stale += 1
    for flag in flags:
        query = {"owner_id": owner(), "transaction_id": flag["transaction_id"], "reason": flag["reason"]}
        if (db().anomaly_records.find_one(query, {"_id": 1})
                or db().anomaly_dismissals.find_one(query, {"_id": 1})):
            continue
        db().anomaly_records.insert_one({**query, "method": flag["method"], "severity": flag["severity"],
                                         "evidence": flag.get("evidence", {}),
                                         "review_status": "pending", "created_at": datetime.now(timezone.utc)})
        created += 1
    return jsonify({"scanned_transactions": len(transactions), "flagged_count": len(flags),
                    "created_count": created, "stale_count": stale,
                    "total_flags": db().anomaly_records.count_documents({"owner_id": owner()})})


@bp.get("")
@jwt_required()
def list_anomalies():
    page = max(1, request.args.get("page", 1, type=int)); limit = min(100, max(1, request.args.get("limit", 25, type=int)))
    q = {"owner_id": owner()}; status = request.args.get("status")
    if status: q["review_status"] = status
    items = []
    for record in db().anomaly_records.find(q).sort("created_at", -1).skip((page-1)*limit).limit(limit):
        transaction_id = oid(record.get("transaction_id", ""))
        transaction = db().transactions.find_one({"_id": transaction_id, "owner_id": owner()},
                                                  {"_id": 0, "date": 1, "description": 1, "reference": 1, "debit": 1, "credit": 1, "final_category": 1}) if transaction_id else None
        item = {**record, "transaction": transaction}
        if transaction:
            item["reason"] = contextualize_legacy_reason(record.get("method"), transaction,
                                                         record.get("reason", ""), record.get("evidence"))
        items.append(serialize(item))
    return jsonify({"items": items, "page": page, "limit": limit, "total": db().anomaly_records.count_documents(q)})


@bp.put("/<anomaly_id>/review")
@jwt_required()
def review(anomaly_id):
    key = oid(anomaly_id); status = (request.get_json(silent=True) or {}).get("status")
    if status not in ("reviewed", "dismissed"): return fail("status must be reviewed or dismissed.")
    result = db().anomaly_records.update_one({"_id": key, "owner_id": owner()}, {"$set": {"review_status": status, "reviewed_at": datetime.now(timezone.utc)}}) if key else None
    return jsonify({"updated": True}) if result and result.matched_count else fail("Anomaly not found.", 404)


@bp.delete("/<anomaly_id>")
@jwt_required()
def dismiss(anomaly_id):
    key = oid(anomaly_id)
    record = db().anomaly_records.find_one({"_id": key, "owner_id": owner()}) if key else None
    if not record:
        return fail("Anomaly not found.", 404)
    db().anomaly_dismissals.update_one(
        {"owner_id": owner(), "transaction_id": record.get("transaction_id"), "reason": record.get("reason")},
        {"$setOnInsert": {"owner_id": owner(), "transaction_id": record.get("transaction_id"),
                           "reason": record.get("reason"), "dismissed_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    db().anomaly_records.delete_one({"_id": key, "owner_id": owner()})
    return "", 204
