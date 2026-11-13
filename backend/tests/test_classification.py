from classification.evaluation import evaluate
from classification.hybrid import classify
from classification.ml_classifier import TransactionClassifier


def test_training_evaluation_reports_both_traditional_models(tmp_path):
    descriptions = ["zomato food delivery", "swiggy dinner order", "restaurant bill", "amazon shopping order", "flipkart product purchase", "myntra clothing shopping"]
    labels = ["Food & Dining"] * 3 + ["Shopping"] * 3
    report = evaluate(descriptions, labels)
    assert "logistic_regression" in report and "multinomial_naive_bayes" in report
    classifier = TransactionClassifier(str(tmp_path), threshold=0.4).train(descriptions, labels)
    assert classifier.predict("zomato food") ["method"] == "ml"


def test_rule_match_precedes_ml():
    class Model:
        threshold = 0.6
        def predict(self, _): raise AssertionError("rule match should short circuit ML")
    result = classify("UPI ZOMATO ORDER", Model())
    assert result["category"] == "Food & Dining"
    assert result["method"] == "rule"
