from pathlib import Path

from classification.ml_classifier import TransactionClassifier
from classification.train_model import retrain_from_feedback


class FeedbackCollection:
    def __init__(self, items): self.items = items; self.saved = None
    def find(self, *_args, **_kwargs): return self.items
    def find_one(self, *_args, **_kwargs): return self.saved
    def insert_one(self, item): self.saved = item


class TransactionCollection:
    def __init__(self, rows): self.rows = rows
    def find_one(self, query, *_args, **_kwargs): return self.rows.get(query["_id"])


class FakeDB:
    def __init__(self, feedback, rows):
        self.model_feedback = FeedbackCollection(feedback)
        self.transactions = TransactionCollection(rows)
        self.model_versions = FeedbackCollection([])


def test_approved_feedback_retrains_and_versions_model(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    feedback = []
    rows = {}
    samples = [("zomato restaurant UPI", "Food & Dining"), ("amazon marketplace purchase", "Shopping"),
               ("uber ride trip", "Transportation"), ("spotify music subscription", "Entertainment"),
               ("monthly electricity bill", "Utilities")]
    for i, (description, label) in enumerate(samples):
        feedback.append({"transaction_id": i, "corrected_category": label})
        rows[i] = {"normalized_description": description, "description": description}
    db = FakeDB(feedback, rows)
    classifier = TransactionClassifier(str(tmp_path), threshold=.5)
    version = retrain_from_feedback(db, classifier, {"MIN_FEEDBACK_FOR_RETRAIN": 5, "MIN_MODEL_F1": .5}, str(repo / "dataset" / "transactions.csv"))
    assert version["version"] == "v1"
    assert version["approved_feedback_count"] == 5
    assert classifier.pipeline is not None
    assert (tmp_path / "classifier.joblib").exists()
