from datetime import datetime, timezone
import json
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .common import db, owner, oid, fail, serialize
from classification.hybrid import classify
from classification.train_model import retrain_from_feedback

bp = Blueprint("classification", __name__, url_prefix="/api/classification")


@bp.post("/predict")
@jwt_required()
def predict():
    body = request.get_json(silent=True) or {}; description = body.get("description")
    if not isinstance(description, str) or not description.strip(): return fail("description is required.")
    result = classify(description, current_app.extensions["bankwise_classifier"], db())
    return jsonify(result)


@bp.get("/metrics")
@jwt_required()
def metrics():
    history = list(db().model_versions.find({}, {"_id": 0}).sort("created_at", -1).limit(10))
    model = history[0] if history else None
    if not model:
        path = os.path.join(current_app.config["MODEL_DIR"], "evaluation.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle: return jsonify({"metrics": json.load(handle), "version": "baseline", "history": [], "available": True})
    return jsonify({"metrics": model.get("metrics") if model else None, "version": model.get("version") if model else None, "history": history, "available": bool(model)})


@bp.get("/summary")
@jwt_required()
def summary():
    owner_id = owner()
    # Compute this small dashboard summary in Python. Older MongoDB versions and
    # legacy documents with mixed field types can reject otherwise valid pipelines.
    projection = {"final_category": 1, "review_required": 1, "review_status": 1,
                  "validation_warnings": 1, "confidence": 1, "method": 1}
    totals = {"total": 0, "review_required": 0, "corrected": 0,
              "extraction_warnings": 0, "confidence_sum": 0.0, "confidence_count": 0}
    category_counts = {}
    for row in db().transactions.find({"owner_id": owner_id}, projection):
        totals["total"] += 1
        warnings = row.get("validation_warnings")
        has_warnings = bool(warnings) if isinstance(warnings, (list, tuple, str)) else False
        status = row.get("review_status")
        needs_review = row.get("review_required") is True or status in ("pending", "needs_review") or has_warnings
        totals["review_required"] += int(needs_review)
        totals["corrected"] += int(status == "corrected")
        totals["extraction_warnings"] += int(has_warnings)
        confidence = row.get("confidence")
        # Keyword rules are deterministic matches, not calibrated model scores.
        if row.get("method") == "ml" and isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            totals["confidence_sum"] += float(confidence)
            totals["confidence_count"] += 1
        category = row.get("final_category") or "Other / Uncategorized"
        category_counts[category] = category_counts.get(category, 0) + 1
    categories = sorted(category_counts.items(), key=lambda item: (-item[1], str(item[0])))
    total = totals["total"]
    confidence_count = totals["confidence_count"]
    average_ml_score = (float(totals.get("confidence_sum", 0)) / confidence_count) if confidence_count else None
    return jsonify({
        "total_transactions": total,
        "review_required": int(totals.get("review_required", 0)),
        "auto_classified": max(0, total - int(totals.get("review_required", 0))),
        "corrected": int(totals.get("corrected", 0)),
        "extraction_warnings": int(totals.get("extraction_warnings", 0)),
        "average_ml_score": average_ml_score,
        "average_confidence": average_ml_score,
        "category_counts": [{"category": category, "count": count} for category, count in categories],
    })


@bp.get("/review-queue")
@jwt_required()
def review_queue():
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(100, max(1, request.args.get("limit", 25, type=int)))
    query = {"owner_id": owner(), "$or": [
        {"review_required": True}, {"review_status": {"$in": ["pending", "needs_review"]}},
        {"validation_warnings": {"$exists": True, "$ne": []}},
    ]}
    collection = db().transactions
    total = collection.count_documents(query)
    items = [serialize(x) for x in collection.find(query).sort([("date", -1), ("_id", 1)]).skip((page - 1) * limit).limit(limit)]
    return jsonify({"items": items, "page": page, "limit": limit, "total": total})


@bp.get("/feedback")
@jwt_required()
def list_feedback():
    user = db().users.find_one({"_id": owner()}, {"role": 1})
    if not user or user.get("role") != "admin": return fail("Administrator access required.", 403)
    page = max(1, request.args.get("page", 1, type=int)); limit = min(100, max(1, request.args.get("limit", 25, type=int)))
    query = {}
    status = request.args.get("status", "pending")
    if status not in ("pending", "approved"): return fail("status must be pending or approved.")
    query["approved"] = status == "approved"
    items = []
    for item in db().model_feedback.find(query).sort("updated_at", -1).skip((page-1)*limit).limit(limit):
        tx = db().transactions.find_one({"_id": item["transaction_id"], "owner_id": item["owner_id"]},
                                        {"date": 1, "description": 1, "debit": 1, "credit": 1}) or {}
        items.append({"id": str(item["_id"]), "transaction": {k: tx.get(k) for k in ("date", "description", "debit", "credit")},
                      "predicted_category": item.get("predicted_category"), "corrected_category": item.get("corrected_category"),
                      "approved": item.get("approved", False), "updated_at": item.get("updated_at")})
    return jsonify({"items": items, "page": page, "limit": limit, "total": db().model_feedback.count_documents(query)})


@bp.post("/retrain")
@jwt_required()
def retrain():
    user = db().users.find_one({"_id": owner()}, {"role": 1})
    if not user or user.get("role") != "admin": return fail("Administrator access required.", 403)
    try:
        version = retrain_from_feedback(db(), current_app.extensions["bankwise_classifier"], current_app.config)
    except ValueError as exc:
        return fail(str(exc), 409)
    return jsonify({"version": version["version"], "metrics": version["metrics"], "candidate_f1": version["candidate_f1"], "baseline_f1": version["baseline_f1"], "approved_feedback_count": version["approved_feedback_count"]})


@bp.put("/feedback/<feedback_id>/approve")
@jwt_required()
def approve_feedback(feedback_id):
    user = db().users.find_one({"_id": owner()}, {"role": 1})
    if not user or user.get("role") != "admin": return fail("Administrator access required.", 403)
    key = oid(feedback_id)
    if not key: return fail("Feedback not found.", 404)
    result = db().model_feedback.update_one({"_id": key}, {"$set": {"approved": True, "approved_by": owner(), "approved_at": datetime.now(timezone.utc)}})
    return jsonify({"approved": True}) if result.matched_count else fail("Feedback not found.", 404)
