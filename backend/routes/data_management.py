import os
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from .common import db, owner, fail

bp = Blueprint("data_management", __name__, url_prefix="/api/data")


@bp.delete("/clear")
@jwt_required()
def clear_imported_data():
    account = owner()
    database = db()
    if database.bank_statements.count_documents({"owner_id": account, "status": "processing"}):
        return fail("A statement is still processing. Wait for it to finish, then reset imported data.", 409)

    upload_root = os.path.realpath(current_app.config["UPLOAD_DIR"])
    files_deleted = files_failed = 0
    statements = list(database.bank_statements.find({"owner_id": account}, {"path": 1}))
    for statement in statements:
        path = statement.get("path")
        if not path:
            continue
        resolved = os.path.realpath(path)
        try:
            if os.path.commonpath([upload_root, resolved]) != upload_root:
                current_app.logger.warning("Skipped statement file outside upload directory during account reset.")
                files_failed += 1
                continue
            if os.path.isfile(resolved):
                os.remove(resolved)
                files_deleted += 1
        except (OSError, ValueError):
            files_failed += 1

    statement_ids = [item["_id"] for item in statements]
    counts = {
        "transactions_deleted": database.transactions.delete_many({"owner_id": account}).deleted_count,
        "statements_deleted": database.bank_statements.delete_many({"owner_id": account}).deleted_count,
        "anomalies_deleted": database.anomaly_records.delete_many({"owner_id": account}).deleted_count,
        "dismissals_deleted": database.anomaly_dismissals.delete_many({"owner_id": account}).deleted_count,
        "feedback_deleted": database.model_feedback.delete_many({"owner_id": account}).deleted_count,
        "processing_logs_deleted": database.processing_logs.delete_many({"owner_id": account}).deleted_count,
        "files_deleted": files_deleted,
        "files_failed": files_failed,
    }
    return jsonify({"cleared": True, **counts})
