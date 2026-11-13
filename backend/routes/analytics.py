from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from .common import db, owner
from analytics.insights import generate_insights

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def transactions(): return list(db().transactions.find({"owner_id": owner()}, {"debit": 1, "credit": 1, "date": 1, "final_category": 1, "description": 1}))


@bp.get("/overview")
@jwt_required()
def overview(): return jsonify(generate_insights(transactions()))


@bp.get("/insights")
@jwt_required()
def insights(): return jsonify(generate_insights(transactions()))


@bp.get("/categories")
@jwt_required()
def categories():
    rows = list(db().transactions.aggregate([{"$match": {"owner_id": owner()}}, {"$group": {"_id": "$final_category", "count": {"$sum": 1}, "debit": {"$sum": "$debit"}, "credit": {"$sum": "$credit"}}}, {"$sort": {"debit": -1}}]))
    return jsonify({"items": [{"category": r["_id"] or "Other / Uncategorized", "count": r["count"], "total_debit": r["debit"], "total_credit": r["credit"]} for r in rows]})


@bp.get("/trends")
@jwt_required()
def trends():
    rows = list(db().transactions.aggregate([{"$match": {"owner_id": owner(), "date": {"$ne": None}}}, {"$addFields": {"month": {"$substrBytes": ["$date", 0, 7]}}}, {"$group": {"_id": "$month", "debit": {"$sum": "$debit"}, "credit": {"$sum": "$credit"}}}, {"$sort": {"_id": 1}}]))
    return jsonify({"items": [{"month": r["_id"], "debit": r["debit"], "credit": r["credit"]} for r in rows]})
