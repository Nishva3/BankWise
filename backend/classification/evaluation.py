from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def make_pipeline(kind="logistic_regression"):
    estimator = LogisticRegression(max_iter=1500, class_weight="balanced") if kind == "logistic_regression" else MultinomialNB(alpha=0.5)
    return Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, strip_accents="unicode")), ("model", estimator)])


def split_data(descriptions, labels):
    counts = Counter(labels)
    stratify = labels if len(counts) > 1 and min(counts.values()) >= 2 else None
    return train_test_split(descriptions, labels, test_size=0.2, random_state=42, stratify=stratify)


def evaluate(descriptions, labels):
    if len(set(labels)) < 2 or len(descriptions) < 4:
        raise ValueError("Evaluation requires at least four examples across two or more categories.")
    x_train, x_test, y_train, y_test = split_data(descriptions, labels)
    output = {}
    for kind in ("logistic_regression", "multinomial_naive_bayes"):
        model = make_pipeline(kind).fit(x_train, y_train)
        pred = model.predict(x_test)
        output[kind] = {"accuracy": float(accuracy_score(y_test, pred)),
                        "weighted_f1": float(f1_score(y_test, pred, average="weighted", zero_division=0)),
                        "report": classification_report(y_test, pred, output_dict=True, zero_division=0),
                        "labels": sorted(set(labels)),
                        "confusion_matrix": confusion_matrix(y_test, pred, labels=sorted(set(labels))).tolist()}
    return {**output, "test_size": len(y_test), "train_size": len(y_train), "split_random_state": 42,
            "stratified": len(set(labels)) > 1 and min(Counter(labels).values()) >= 2}
