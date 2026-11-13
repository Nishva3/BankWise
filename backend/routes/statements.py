import hashlib
import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from pymongo import ReturnDocument
from .common import db, owner, oid, serialize, fail
from database.schemas import statement_document, transaction_document
from services.processing_service import process_statement
from analytics.anomaly_detector import detect
from services.deduplication import deduplicate_owner_transactions, transaction_fingerprint

bp = Blueprint("statements", __name__, url_prefix="/api/statements")


def _stream_sha256(stream):
    digest = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    stream.seek(0)
    return digest.hexdigest()


def _path_sha256(path):
    try:
        with open(path, "rb") as stream:
            return _stream_sha256(stream)
    except OSError:
        return None


@bp.post("/upload")
@jwt_required()
def upload():
    file = request.files.get("file")
    if not file or not file.filename: return fail("PDF file field 'file' is required.")
    if not file.filename.lower().endswith(".pdf") or file.mimetype not in ("application/pdf", "application/octet-stream"): return fail("Only PDF uploads are supported.")
    header = file.stream.read(1024); file.stream.seek(0)
    if b"%PDF-" not in header: return fail("Uploaded file does not have a valid PDF header.")
    file_hash = _stream_sha256(file.stream)
    matches = []
    for previous in db().bank_statements.find({"owner_id": owner()}):
        previous_hash = previous.get("file_sha256") or _path_sha256(previous.get("path", ""))
        if previous_hash == file_hash:
            matches.append(previous)
            if not previous.get("file_sha256"):
                db().bank_statements.update_one({"_id": previous["_id"]}, {"$set": {"file_sha256": file_hash}})
    if matches:
        deduplicate_owner_transactions(db(), owner())
        canonical = sorted(matches, key=lambda x: (x.get("status") != "completed", -int(x.get("transaction_count") or 0), x.get("created_at")))[0]
        # Do not preserve an earlier false-success record with zero imported rows.
        # Reopen it so the corrected layout-aware extractor gets another attempt.
        if canonical.get("status") == "completed" and int(canonical.get("transaction_count") or 0) == 0:
            db().bank_statements.update_one(
                {"_id": canonical["_id"], "owner_id": owner()},
                {"$set": {"status": "failed", "error": "Previous extraction completed without transaction rows; retrying with the current parser.", "updated_at": datetime.now(timezone.utc)}}
            )
            canonical["status"] = "failed"
        return jsonify({"statement_id": str(canonical["_id"]), "status": canonical["status"],
                        "transaction_count": canonical.get("transaction_count", 0), "duplicate_count": canonical.get("duplicate_count", 0),
                        "duplicate": True}), 200
    directory = current_app.config["UPLOAD_DIR"]; os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{uuid.uuid4().hex}.pdf")
    file.save(path)
    doc = statement_document(owner(), os.path.basename(file.filename), path, file_sha256=file_hash)
    result = db().bank_statements.insert_one(doc)
    return jsonify({"statement_id": str(result.inserted_id), "status": "uploaded"}), 201


@bp.get("")
@jwt_required()
def list_statements():
    items = [serialize(x) for x in db().bank_statements.find({"owner_id": owner()}).sort("created_at", -1).limit(100)]
    return jsonify({"items": items})


@bp.get("/<statement_id>")
@jwt_required()
def get_statement(statement_id):
    key = oid(statement_id); doc = db().bank_statements.find_one({"_id": key, "owner_id": owner()}) if key else None
    return jsonify({"statement": serialize(doc)}) if doc else fail("Statement not found.", 404)


@bp.get("/<statement_id>/status")
@jwt_required()
def status(statement_id): return get_statement(statement_id)


@bp.post("/<statement_id>/process")
@jwt_required()
def process(statement_id):
    key = oid(statement_id); statement = db().bank_statements.find_one({"_id": key, "owner_id": owner()}) if key else None
    if not statement: return fail("Statement not found.", 404)
    if statement.get("status") == "completed": return jsonify({"statement_id": statement_id, "status": "completed", "transaction_count": statement.get("transaction_count", 0), "duplicate_count": statement.get("duplicate_count", 0)})
    statement = db().bank_statements.find_one_and_update(
        {"_id": key, "owner_id": owner(), "status": {"$in": ["uploaded", "failed"]}},
        {"$set": {"status": "processing", "updated_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER
    )
    if not statement:
        latest = db().bank_statements.find_one({"_id": key, "owner_id": owner()})
        if latest and latest.get("status") == "completed":
            return jsonify({"statement_id": statement_id, "status": "completed", "transaction_count": latest.get("transaction_count", 0), "duplicate_count": latest.get("duplicate_count", 0)})
        return fail("Statement is already being processed or is not in a processable state.", 409)
    try:
        # A previous failed attempt may have inserted only part of the statement.
        db().transactions.delete_many({"statement_id": key, "owner_id": owner()})
        db().anomaly_records.delete_many({"statement_id": key, "owner_id": owner()})
        result = process_statement(statement["path"], current_app.extensions["bankwise_classifier"], current_app.config, db())
        account_number = result["parsed"].get("account_number")
        if account_number:
            raw_account = str(account_number).replace(" ", "").replace("-", "")
            result["parsed"]["account_number"] = "*" * max(0, len(raw_account) - 4) + raw_account[-4:]
        deduplication = deduplicate_owner_transactions(db(), owner())
        known = set(deduplication["fingerprints"])
        tx_ids = []; accepted_rows = []; skipped_duplicates = 0
        historical = list(db().transactions.find({"owner_id": owner(), "statement_id": {"$ne": key}}))
        for tx in result["transactions"]:
            fingerprint = transaction_fingerprint(tx)
            if fingerprint and fingerprint in known:
                skipped_duplicates += 1
                continue
            tx_doc = transaction_document(owner(), key, tx)
            if fingerprint: tx_doc["fingerprint"] = fingerprint
            try:
                tx_id = db().transactions.insert_one(tx_doc).inserted_id
            except Exception as exc:
                from pymongo.errors import DuplicateKeyError
                if isinstance(exc, DuplicateKeyError) and fingerprint:
                    skipped_duplicates += 1
                    continue
                raise
            tx_ids.append(tx_id); accepted_rows.append({**tx, "_id": tx_id})
            if fingerprint: known.add(fingerprint)
        anomalies = detect(accepted_rows, historical)
        for anomaly in anomalies:
            anomaly.update({"statement_id": key, "owner_id": owner(), "created_at": datetime.now(timezone.utc)})
            db().anomaly_records.insert_one(anomaly)
        validation = {**result["validation"], "warnings": result["warnings"], "errors": []}
        db().bank_statements.update_one({"_id": key}, {"$set": {"status": "completed", "result": {k:v for k,v in result.items() if k != "transactions"}, "validation": validation, "transaction_count": len(tx_ids), "duplicate_count": skipped_duplicates, "updated_at": datetime.now(timezone.utc)}})
        db().processing_logs.insert_one({"owner_id": owner(), "statement_id": key, "stage": "processing", "status": "completed", "transaction_count": len(tx_ids), "duplicate_count": skipped_duplicates, "warning_count": len(result["warnings"]), "created_at": datetime.now(timezone.utc)})
        return jsonify({"statement_id": statement_id, "status": "completed", "transaction_count": len(tx_ids), "duplicate_count": skipped_duplicates, "warnings": result["warnings"]})
    except Exception as exc:
        current_app.logger.exception("Statement processing failed")
        db().bank_statements.update_one({"_id": key}, {"$set": {"status": "failed", "error": str(exc)[:300], "updated_at": datetime.now(timezone.utc)}})
        db().processing_logs.insert_one({"owner_id": owner(), "statement_id": key, "stage": "processing", "status": "failed", "error_code": type(exc).__name__, "created_at": datetime.now(timezone.utc)})
        if isinstance(exc, ValueError) and str(exc).startswith("No transactions could be read"):
            return fail(str(exc), 422)
        return fail("Statement processing failed. Check the PDF and OCR configuration.", 422)


@bp.delete("/<statement_id>")
@jwt_required()
def delete_statement(statement_id):
    key = oid(statement_id)
    statement = db().bank_statements.find_one({"_id": key, "owner_id": owner()}) if key else None
    if not statement: return fail("Statement not found.", 404)
    db().bank_statements.delete_one({"_id": key, "owner_id": owner()})
    db().transactions.delete_many({"statement_id": key, "owner_id": owner()}); db().anomaly_records.delete_many({"statement_id": key, "owner_id": owner()})
    db().model_feedback.delete_many({"statement_id": key, "owner_id": owner()})
    db().processing_logs.delete_many({"statement_id": key, "owner_id": owner()})
    try:
        if os.path.isfile(statement.get("path", "")): os.remove(statement["path"])
    except OSError:
        current_app.logger.warning("Could not remove a deleted statement's stored PDF.")
    return "", 204
