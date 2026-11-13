import os
import json
from pathlib import Path
import tempfile
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.metrics import f1_score

from classification.evaluation import evaluate, make_pipeline, split_data


def retrain_from_feedback(db, classifier, config, dataset_path="dataset/transactions.csv"):
    approved = list(db.model_feedback.find({"approved": True}, {"transaction_id": 1, "corrected_category": 1}))
    minimum = int(config["MIN_FEEDBACK_FOR_RETRAIN"])
    if len(approved) < minimum:
        raise ValueError(f"At least {minimum} approved corrections are required; found {len(approved)}.")
    base = load_dataset(dataset_path)
    feedback_rows = []
    for item in approved:
        tx = db.transactions.find_one({"_id": item["transaction_id"]}, {"normalized_description": 1, "description": 1})
        description = (tx or {}).get("normalized_description") or (tx or {}).get("description")
        label = item.get("corrected_category")
        if description and label:
            feedback_rows.append({"description": str(description), "category": str(label)})
    if len(feedback_rows) < minimum:
        raise ValueError("Approved feedback no longer points to enough available transactions.")
    data = pd.concat([base, pd.DataFrame(feedback_rows)], ignore_index=True)
    descriptions, labels = data.description.tolist(), data.category.tolist()
    report = evaluate(descriptions, labels)
    x_train, x_test, y_train, y_test = split_data(descriptions, labels)
    candidate = make_pipeline("logistic_regression").fit(x_train, y_train)
    candidate_f1 = float(f1_score(y_test, candidate.predict(x_test), average="weighted", zero_division=0))
    baseline_f1 = None
    if classifier.pipeline is not None:
        baseline_f1 = float(f1_score(y_test, classifier.pipeline.predict(x_test), average="weighted", zero_division=0))
    minimum_f1 = float(config["MIN_MODEL_F1"])
    if candidate_f1 < minimum_f1 or (baseline_f1 is not None and candidate_f1 < baseline_f1):
        raise ValueError("Candidate model did not meet the minimum F1 and no-regression promotion criteria.")
    promoted = make_pipeline("logistic_regression").fit(descriptions, labels)
    folder = os.path.dirname(classifier.path) or "."
    os.makedirs(folder, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="candidate-", suffix=".joblib", dir=folder)
    os.close(fd)
    try:
        joblib.dump(promoted, temporary)
        os.replace(temporary, classifier.path)
    finally:
        if os.path.exists(temporary): os.remove(temporary)
    classifier.pipeline = promoted
    previous = db.model_versions.find_one(sort=[("version_number", -1)]) or {}
    number = int(previous.get("version_number", 0)) + 1
    classifier.model_version = f"v{number}"
    metrics = report["logistic_regression"]
    model_doc = {"version_number": number, "version": f"v{number}", "algorithm": "TF-IDF + LogisticRegression",
                 "created_at": datetime.now(timezone.utc), "metrics": metrics,
                 "baseline_f1": baseline_f1, "candidate_f1": candidate_f1,
                 "approved_feedback_count": len(feedback_rows), "training_rows": len(data)}
    db.model_versions.insert_one(model_doc)
    return model_doc


def load_dataset(path="dataset/transactions.csv"):
    source = Path(path)
    if not source.exists(): source = Path(__file__).resolve().parents[2] / "dataset" / "transactions.csv"
    data = pd.read_csv(source).dropna(subset=["description", "category"])
    data["description"] = data["description"].astype(str).str.strip()
    data["category"] = data["category"].astype(str).str.strip()
    return data[data.description.ne("") & data.category.ne("")]


def train_dataset(path="dataset/transactions.csv", model_dir="models"):
    data = load_dataset(path)
    report = evaluate(data.description.tolist(), data.category.tolist())
    model = make_pipeline("logistic_regression").fit(data.description.tolist(), data.category.tolist())
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, "classifier.joblib"))
    report["dataset_rows"] = len(data)
    report["categories"] = sorted(data.category.unique().tolist())
    with open(os.path.join(model_dir, "evaluation.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    return report


if __name__ == "__main__":
    import json
    print(json.dumps(train_dataset(), indent=2))
