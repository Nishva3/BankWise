import re
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo import ReturnDocument
from werkzeug.security import generate_password_hash, check_password_hash
from .common import db, owner, serialize, fail

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    body = request.get_json(silent=True) or {}; email = str(body.get("email", "")).strip().lower(); password = str(body.get("password", ""))
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): return fail("A valid email is required.")
    if len(password) < 10: return fail("Password must be at least 10 characters.")
    name = str(body.get("name", "")).strip() or email.split("@", 1)[0]
    if len(name) > 120: return fail("name must be at most 120 characters.")
    role = "admin" if email in current_app.config["ADMIN_EMAILS"] else "user"
    user = {"email": email, "name": name, "phone": "", "institution": "", "city": "", "role": role,
            "password_hash": generate_password_hash(password, method="scrypt"), "created_at": datetime.now(timezone.utc)}
    try: result = db().users.insert_one(user)
    except Exception: return fail("An account with this email may already exist.", 409)
    return jsonify({"user": {"id": str(result.inserted_id), "email": email}}), 201


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}; user = db().users.find_one({"email": str(body.get("email", "")).strip().lower()})
    if not user or not check_password_hash(user["password_hash"], str(body.get("password", ""))): return fail("Invalid email or password.", 401)
    return jsonify({"access_token": create_access_token(identity=str(user["_id"])), "token_type": "Bearer", "expires_in": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]})


@bp.get("/me")
@jwt_required()
def me():
    user = db().users.find_one({"_id": owner()})
    return jsonify({"user": _public_user(user)}) if user else fail("User not found.", 404)


def _public_user(user):
    return {"id": str(user["_id"]), "email": user["email"],
            "name": user.get("name") or user["email"].split("@", 1)[0],
            "phone": user.get("phone", ""), "institution": user.get("institution", ""),
            "city": user.get("city", "")}


@bp.patch("/me")
@jwt_required()
def update_me():
    body = request.get_json(silent=True) or {}
    fields = {"name": (120, True), "phone": (40, False), "institution": (120, False), "city": (100, False)}
    updates = {}
    for key, (limit, required) in fields.items():
        if key not in body:
            continue
        value = body[key]
        if not isinstance(value, str):
            return fail(f"{key} must be text.")
        value = value.strip()
        if (required and not value) or len(value) > limit:
            return fail(f"{key} must be {'1 to ' if required else 'at most '}{limit} characters.")
        updates[key] = value
    if not updates:
        return fail("At least one profile field is required.")
    updates["updated_at"] = datetime.now(timezone.utc)
    user = db().users.find_one_and_update({"_id": owner()}, {"$set": updates}, return_document=ReturnDocument.AFTER)
    return jsonify({"user": _public_user(user)}) if user else fail("User not found.", 404)
