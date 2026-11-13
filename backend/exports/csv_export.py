import io
import pandas as pd


def make_csv(transactions):
    fields = ["date", "description", "debit", "credit", "balance", "final_category", "method", "confidence"]
    df = pd.DataFrame([{k: t.get(k) for k in fields} for t in transactions], columns=fields)
    df.rename(columns={"final_category": "category", "method": "classification_method", "confidence": "confidence_score"}, inplace=True)
    stream = io.StringIO(); df.to_csv(stream, index=False); return stream.getvalue()
