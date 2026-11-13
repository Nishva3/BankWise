from datetime import datetime, timezone
import json
import os
from bson import ObjectId
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException
from config import Config
from database.mongo import Database
from classification.ml_classifier import TransactionClassifier
from routes import register_blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, origins=app.config["CORS_ORIGINS"])
    JWTManager(app)
    database = Database(app.config["MONGO_URI"])
    try:
        database.init_indexes()
        _register_baseline_model(database.db, app.config["MODEL_DIR"])
    except Exception:
        app.logger.warning("MongoDB index initialization deferred; database is not reachable yet.")
    app.extensions["bankwise_db"] = database.db
    classifier = TransactionClassifier(app.config["MODEL_DIR"], app.config["CLASSIFICATION_THRESHOLD"])
    try:
        current_model = database.db.model_versions.find_one(sort=[("version_number", -1)])
        if current_model: classifier.model_version = current_model.get("version", classifier.model_version)
    except Exception:
        app.logger.warning("Could not read the current model version from MongoDB.")
    app.extensions["bankwise_classifier"] = classifier
    app.extensions["bankwise_config"] = app.config

    @app.get("/health")
    def health():
        try: database.client.admin.command("ping")
        except Exception: return jsonify({"ok": False, "error": "database_unavailable"}), 503
        return jsonify({"ok": True})

    @app.errorhandler(Exception)
    def handle_error(error):
        if isinstance(error, HTTPException): return jsonify({"error": error.name.lower().replace(" ", "_"), "message": error.description}), error.code
        app.logger.exception("Unhandled request failure")
        return jsonify({"error": "internal_server_error", "message": "The request could not be completed."}), 500

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    register_blueprints(app)
    return app


def _register_baseline_model(db, model_dir):
    path = os.path.join(model_dir, "evaluation.json")
    if not os.path.isfile(path): return
    with open(path, encoding="utf-8") as handle: report = json.load(handle)
    logistic = report.get("logistic_regression")
    if not logistic: return
    db.model_versions.update_one({"version": "baseline"}, {"$setOnInsert": {
        "version_number": 0, "version": "baseline", "algorithm": "TF-IDF + LogisticRegression",
        "created_at": datetime.now(timezone.utc), "metrics": logistic,
        "comparison_metrics": {key: report[key] for key in ("logistic_regression", "multinomial_naive_bayes") if key in report},
        "training_rows": report.get("dataset_rows"), "categories": report.get("categories", [])
    }}, upsert=True)


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
