from bson import ObjectId
from flask import current_app, jsonify
from flask_jwt_extended import get_jwt_identity


def db(): return current_app.extensions["bankwise_db"]
def owner(): return ObjectId(get_jwt_identity())
def oid(value): return ObjectId(value) if ObjectId.is_valid(value) else None
def fail(message, status=400): return jsonify({"error": message}), status
def serialize(document):
    if not document: return None
    return {k: (str(v) if isinstance(v, ObjectId) else v.isoformat() if hasattr(v, "isoformat") else v) for k, v in document.items() if k not in ("password_hash", "path")}
