from .rule_engine import classify_rule


def classify(description, classifier, db=None, rules=None):
    result = classify_rule(description, db, rules) or classifier.predict(description)
    result.setdefault("review_required", result["confidence"] < getattr(classifier, "threshold", 0.55))
    result["predicted_category"] = result["category"]
    result["final_category"] = result["category"]
    result["review_status"] = "pending" if result["review_required"] else "not_required"
    result["model_version"] = getattr(classifier, "model_version", "untrained")
    return result
