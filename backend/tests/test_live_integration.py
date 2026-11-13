import io
import os
import uuid
from urllib.parse import urlsplit, urlunsplit

import fitz
import pytest
from pymongo import MongoClient

from app import create_app
from config import Config


@pytest.fixture
def live_client(tmp_path):
    base_uri = os.getenv("MONGO_TEST_URI", "mongodb://localhost:27017")
    probe = MongoClient(base_uri, serverSelectionTimeoutMS=900)
    try:
        probe.admin.command("ping")
    except Exception:
        probe.close()
        pytest.skip("MongoDB test service is not available")
    db_name = "bankwise_test_" + uuid.uuid4().hex
    parts = urlsplit(base_uri)
    uri = urlunsplit((parts.scheme, parts.netloc, "/" + db_name, parts.query, parts.fragment))

    class TestConfig(Config):
        MONGO_URI = uri
        SECRET_KEY = "bankwise-integration-test-signing-secret"
        JWT_SECRET_KEY = SECRET_KEY
        UPLOAD_DIR = str(tmp_path / "uploads")
        MODEL_DIR = str((__import__("pathlib").Path(__file__).resolve().parents[1] / "models"))
        ADMIN_EMAILS = ["admin@bankwise.test"]
        TESTING = True

    app = create_app(TestConfig)
    try:
        yield app.test_client()
    finally:
        probe.drop_database(db_name)
        probe.close()


def _token(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": "a-long-test-password"})
    assert response.status_code == 200
    return response.json["access_token"]


def test_live_registration_upload_processing_ownership_edit_and_export(live_client):
    client = live_client
    first_email = "user-" + uuid.uuid4().hex + "@bankwise.test"
    assert client.post("/api/auth/register", json={"email": first_email, "password": "a-long-test-password"}).status_code == 201
    token = _token(client, first_email)
    baseline_metrics = client.get("/api/classification/metrics", headers={"Authorization": "Bearer " + token})
    assert baseline_metrics.status_code == 200 and baseline_metrics.json["version"] == "baseline"
    invalid_pdf = client.post("/api/statements/upload", headers={"Authorization": "Bearer " + token}, data={"file": (io.BytesIO(b"not a pdf"), "bad.pdf", "application/pdf")}, content_type="multipart/form-data")
    assert invalid_pdf.status_code == 400
    doc = fitz.open(); page = doc.new_page()
    page.insert_text((40, 45), "HDFC Bank Statement\nAccount Number: 123456789012\nOpening Balance: 1000.00\nClosing Balance: 550.00\n01/04/2025 UPI SWIGGY 450.00 Dr 550.00", fontsize=11)
    pdf_bytes = doc.tobytes(); doc.close()
    uploaded = client.post("/api/statements/upload", headers={"Authorization": "Bearer " + token}, data={"file": (io.BytesIO(pdf_bytes), "statement.pdf", "application/pdf")}, content_type="multipart/form-data")
    assert uploaded.status_code == 201
    statement_id = uploaded.json["statement_id"]
    processed = client.post(f"/api/statements/{statement_id}/process", headers={"Authorization": "Bearer " + token})
    assert processed.status_code == 200, processed.json
    retried = client.post(f"/api/statements/{statement_id}/process", headers={"Authorization": "Bearer " + token})
    assert retried.status_code == 200 and retried.json["transaction_count"] == 1
    status = client.get(f"/api/statements/{statement_id}/status", headers={"Authorization": "Bearer " + token}).json["statement"]
    assert status["status"] == "completed"
    assert status["result"]["validation"]["balance_reconciliation"]["reconciled"] is True
    assert status["validation"]["balance_reconciliation"]["reconciled"] is True
    assert "123456789012" not in str(status)
    transactions = client.get("/api/transactions", headers={"Authorization": "Bearer " + token}).json
    assert transactions["total"] == 1
    tx = transactions["items"][0]
    assert tx["final_category"] == "Food & Dining"
    assert client.get("/api/analytics/overview", headers={"Authorization": "Bearer " + token}).status_code == 200

    second_email = "user-" + uuid.uuid4().hex + "@bankwise.test"
    client.post("/api/auth/register", json={"email": second_email, "password": "a-long-test-password"})
    second_token = _token(client, second_email)
    assert client.get("/api/transactions/" + tx["_id"], headers={"Authorization": "Bearer " + second_token}).status_code == 404
    bad_edit = client.put("/api/transactions/" + tx["_id"], headers={"Authorization": "Bearer " + token}, json={"debit": "not money"})
    assert bad_edit.status_code == 400
    description_edit = client.put("/api/transactions/" + tx["_id"], headers={"Authorization": "Bearer " + token}, json={"description": "UPI SWIGGY FOOD"})
    assert description_edit.status_code == 200
    assert description_edit.json["transaction"]["normalized_description"] == "upi swiggy food"

    edit = client.put("/api/transactions/" + tx["_id"], headers={"Authorization": "Bearer " + token}, json={"category": "Groceries"})
    assert edit.status_code == 200
    feedback_id = client.application.extensions["bankwise_db"].model_feedback.find_one({"transaction_id": __import__("bson").ObjectId(tx["_id"])})["_id"]
    admin_email = "admin@bankwise.test"
    client.post("/api/auth/register", json={"email": admin_email, "password": "a-long-test-password"})
    admin_token = _token(client, admin_email)
    assert client.get("/api/classification/feedback", headers={"Authorization": "Bearer " + token}).status_code == 403
    approved = client.put(f"/api/classification/feedback/{feedback_id}/approve", headers={"Authorization": "Bearer " + admin_token})
    assert approved.status_code == 200
    feedback_page = client.get("/api/classification/feedback?status=approved", headers={"Authorization": "Bearer " + admin_token}).json
    assert feedback_page["total"] == 1
    assert client.post("/api/classification/retrain", headers={"Authorization": "Bearer " + token}).status_code == 403
    assert client.post("/api/classification/retrain", headers={"Authorization": "Bearer " + admin_token}).status_code == 409
    assert client.get("/api/export/csv?statement_id=" + statement_id, headers={"Authorization": "Bearer " + token}).status_code == 200
    assert client.get("/api/export/excel?statement_id=" + statement_id, headers={"Authorization": "Bearer " + token}).data[:2] == b"PK"
    stored_pdf = client.application.extensions["bankwise_db"].bank_statements.find_one({"_id": __import__("bson").ObjectId(statement_id)})["path"]
    assert client.delete(f"/api/statements/{statement_id}", headers={"Authorization": "Bearer " + token}).status_code == 204
    assert not os.path.exists(stored_pdf)
