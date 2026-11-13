import os
import joblib
from classification.evaluation import make_pipeline


class TransactionClassifier:
    def __init__(self, model_dir="models", threshold=0.55):
        self.path = os.path.join(model_dir, "classifier.joblib")
        self.threshold = threshold
        self.pipeline = None
        if os.path.exists(self.path): self.pipeline = joblib.load(self.path)
        self.model_version = "baseline" if self.pipeline is not None else "untrained"

    def predict(self, description):
        if not self.pipeline: return {"category": "Other / Uncategorized", "method": "fallback", "confidence": 0.0, "review_required": True}
        probs = self.pipeline.predict_proba([description or ""])[0]
        idx = probs.argmax(); confidence = float(probs[idx])
        return {"category": self.pipeline.classes_[idx] if confidence >= self.threshold else "Other / Uncategorized", "method": "ml", "confidence": confidence, "review_required": confidence < self.threshold}

    def train(self, descriptions, labels):
        if len(set(labels)) < 2: raise ValueError("At least two categories are required to train the classifier.")
        self.pipeline = make_pipeline("logistic_regression")
        self.pipeline.fit(descriptions, labels)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        joblib.dump(self.pipeline, self.path)
        self.model_version = "trained"
        return self
