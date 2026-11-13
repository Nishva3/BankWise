from datetime import datetime, timezone
import math
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from .common import db, owner, oid, serialize, fail
from analytics.insights import generate_insights
from classification.rule_engine import CATEGORIES
from classification.hybrid import classify
from extraction.data_cleaner import normalize_date, parse_amount
from services.deduplication import deduplicate_owner_transactions

bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


def _transaction_query(args):
    query = {"owner_id": owner()}
    category = args.get("category")
    statement = oid(args.get("statement_id", ""))
    if category: query["final_category"] = category
    if statement: query["statement_id"] = statement
    date_from = args.get("date_from"); date_to = args.get("date_to")
    if date_from or date_to:
        query["date"] = {}
        if date_from: query["date"]["$gte"] = date_from
        if date_to: query["date"]["$lte"] = date_to
    search = args.get("search", "").strip()
    if search: query["description"] = {"$regex": re.escape(search), "$options": "i"}
    return query


@bp.get("")
@jwt_required()
def list_transactions():
    query = _transaction_query(request.args)
    page = max(1, request.args.get("page", 1, type=int)); limit = min(100, max(1, request.args.get("limit", 25, type=int)))
    total = db().transactions.count_documents(query)
    items = [serialize(t) for t in db().transactions.find(query).sort("date", -1).skip((page-1)*limit).limit(limit)]
    return jsonify({"items": items, "page": page, "limit": limit, "total": total})


@bp.get("/summary")
@jwt_required()
def transaction_summary():
    query = _transaction_query(request.args)
    rows = list(db().transactions.find(query, {"debit": 1, "credit": 1, "description": 1,
                                                "date": 1, "final_category": 1}))
    totals = generate_insights(rows) if rows else {}
    return jsonify({"count": len(rows),
                    "debit_total": float(totals.get("gross_expenditure", 0)),
                    "credit_total": float(totals.get("total_credits", 0)),
                    "net_cash_flow": float(totals.get("net_cash_flow", 0)),
                    "recognized_income_total": float(totals.get("total_income", 0))})


@bp.post("/reclassify")
@jwt_required()
def reclassify_transactions():
    """Re-run the active classifier for a user's transactions, preserving corrections."""
    classifier = current_app.extensions["bankwise_classifier"]
    custom_rules = list(db().classification_rules.find({"enabled": True}).sort("priority", -1))
    docs = db().transactions.find({"owner_id": owner(), "review_status": {"$ne": "corrected"}})
    processed = 0
    changed = 0
    for tx in docs:
        result = classify(tx.get("description", ""), classifier, db(), custom_rules)
        fields = {key: result[key] for key in ("predicted_category", "final_category", "method", "confidence", "review_required", "review_status") if key in result}
        fields["updated_at"] = datetime.now(timezone.utc)
        processed += 1
        changed += db().transactions.update_one({"_id": tx["_id"], "owner_id": owner()}, {"$set": fields}).modified_count
    return jsonify({"processed_count": processed, "changed_count": changed})


@bp.post("/deduplicate")
@jwt_required()
def deduplicate_transactions():
    result = deduplicate_owner_transactions(db(), owner())
    return jsonify({"removed_count": result["removed_count"]})


@bp.get("/<transaction_id>")
@jwt_required()
def get_transaction(transaction_id):
    key = oid(transaction_id); tx = db().transactions.find_one({"_id": key, "owner_id": owner()}) if key else None
    return jsonify({"transaction": serialize(tx)}) if tx else fail("Transaction not found.", 404)


@bp.put("/<transaction_id>")
@jwt_required()
def update_transaction(transaction_id):
    key = oid(transaction_id); tx = db().transactions.find_one({"_id": key, "owner_id": owner()}) if key else None
    if not tx: return fail("Transaction not found.", 404)
    body = request.get_json(silent=True) or {}; updates = {}
    if "description" in body:
        description = body["description"]
        if not isinstance(description, str) or not description.strip() or len(description) > 500: return fail("description must be 1 to 500 characters.")
        updates.update({"description": description.strip(), "normalized_description": re.sub(r"[^a-z0-9 ]", " ", description.lower()).strip()})
    if "date" in body:
        if body["date"] is not None and not isinstance(body["date"], str): return fail("date must be text.")
        normalized = normalize_date(body["date"])
        if body["date"] and not normalized: return fail("date must use a supported date format.")
        updates["date"] = normalized
    for field in ("debit", "credit", "balance"):
        if field in body:
            value = body[field]
            if isinstance(value, bool): return fail(f"{field} must be numeric.")
            if value is None or value == "": updates[field] = None
            else:
                if isinstance(value, str) and not re.search(r"\d", value): return fail(f"{field} must be numeric.")
                try: number = parse_amount(value)
                except (TypeError, ValueError): return fail(f"{field} must be numeric.")
                if not math.isfinite(number): return fail(f"{field} must be finite.")
                updates[field] = number
    if "reference" in body:
        reference = body["reference"]
        if reference is not None and (not isinstance(reference, str) or len(reference) > 100): return fail("reference must be at most 100 characters.")
        updates["reference"] = reference
    if "category" in body:
        category = str(body["category"])
        if category not in CATEGORIES: return fail("Invalid category.")
        updates.update({"final_category": category, "corrected_category": category, "review_status": "corrected"})
        feedback = {"owner_id": owner(), "transaction_id": key, "statement_id": tx["statement_id"], "predicted_category": tx.get("predicted_category"), "corrected_category": category, "approved": False, "updated_at": datetime.now(timezone.utc)}
        db().model_feedback.update_one({"owner_id": owner(), "transaction_id": key}, {"$set": feedback}, upsert=True)
    elif "description" in updates and tx.get("review_status") != "corrected":
        result = classify(updates["normalized_description"], current_app.extensions["bankwise_classifier"], db())
        updates.update({"predicted_category": result["predicted_category"], "final_category": result["final_category"],
                        "method": result["method"], "confidence": result["confidence"], "review_required": result["review_required"],
                        "review_status": result["review_status"]})
    updates["updated_at"] = datetime.now(timezone.utc)
    update = {"$set": updates}
    if any(field in updates for field in ("date", "description", "debit", "credit", "balance", "reference")):
        update["$unset"] = {"fingerprint": ""}
    db().transactions.update_one({"_id": key, "owner_id": owner()}, update)
    return jsonify({"transaction": serialize(db().transactions.find_one({"_id": key}))})


@bp.delete("/<transaction_id>")
@jwt_required()
def delete_transaction(transaction_id):
    key = oid(transaction_id)
    if not key or not db().transactions.delete_one({"_id": key, "owner_id": owner()}).deleted_count: return fail("Transaction not found.", 404)
    db().model_feedback.delete_many({"owner_id": owner(), "transaction_id": key})
    db().anomaly_records.delete_many({"owner_id": owner(), "transaction_id": str(key)})
    return "", 204
