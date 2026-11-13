from collections import Counter, defaultdict
from difflib import SequenceMatcher
import re

import pandas as pd


def _amount_direction(tx):
    debit, credit = abs(float(tx.get("debit") or 0)), abs(float(tx.get("credit") or 0))
    return (debit, "debit") if debit else (credit, "credit") if credit else (0.0, "none")


def _similar(a, b):
    return SequenceMatcher(None, str(a or "").lower(), str(b or "").lower()).ratio() >= .88


def _transaction_label(tx, fallback="transaction"):
    description = re.sub(r"\s+", " ", str(tx.get("description") or "")).strip() or fallback
    date = str(tx.get("date") or "date unavailable")
    reference = str(tx.get("reference") or "")
    ref_text = f" (reference {reference})" if reference else ""
    return f"{description} on {date}{ref_text}"


def contextualize_legacy_reason(method, transaction, reason, evidence=None):
    """Build a transaction-specific explanation for current and legacy anomaly rows."""
    evidence = evidence if isinstance(evidence, dict) else {}
    debit = max(0.0, float(transaction.get("debit") or 0))
    credit = max(0.0, float(transaction.get("credit") or 0))
    amount = debit or credit
    label = _transaction_label(transaction)
    if method == "IQR":
        threshold = evidence.get("threshold")
        limit = f"the statement's upper IQR limit of INR {float(threshold):,.2f}" if isinstance(threshold, (int, float)) else "the statement's usual debit range"
        return f"{label}: debit INR {debit:,.2f} is above {limit}."
    if method == "Z-score":
        threshold = evidence.get("threshold")
        limit = f"the three-standard-deviation limit of INR {float(threshold):,.2f}" if isinstance(threshold, (int, float)) else "three standard deviations above the statement's average debit"
        return f"{label}: debit INR {debit:,.2f} is above {limit}."
    if method == "historical_average_deviation":
        average = evidence.get("historical_average_debit")
        comparison = f"the previous average debit of INR {float(average):,.2f}" if isinstance(average, (int, float)) else "the prior statements' average debit"
        return f"{label}: debit INR {debit:,.2f} is more than three times {comparison}."
    if method == "transaction_frequency":
        month = evidence.get("month") or str(transaction.get("date") or "")[:7] or "the statement month"
        count = evidence.get("monthly_count")
        quantity = f"{int(count)} times" if isinstance(count, (int, float)) else "at least 8 times"
        return f"{label}: this merchant description appears {quantity} during {month}; the review threshold is 8 in one month."
    if method == "date_amount_direction_description_reference":
        matched = evidence.get("matched_description") or "another transaction with the same date, amount, and direction"
        matched_date = evidence.get("matched_date")
        match_text = f" ({matched} on {matched_date})" if matched_date else f" ({matched})"
        return f"{label}: INR {amount:,.2f} may duplicate{match_text}."
    if method == "cross_statement_duplicate":
        matched = evidence.get("matched_description") or "a transaction in another statement"
        matched_date = evidence.get("matched_date")
        match_text = f" ({matched} on {matched_date})" if matched_date else f" ({matched})"
        return f"{label}: INR {amount:,.2f} may duplicate{match_text}."
    return reason


def detect(transactions, historical=()):
    flags = []
    current_debits = [max(0.0, float(t.get("debit") or 0)) for t in transactions]
    series = pd.Series(current_debits, dtype=float)
    q1, q3 = series.quantile(.25), series.quantile(.75)
    iqr_cutoff = q3 + 1.5 * (q3-q1)
    mean, std = float(series.mean()), float(series.std(ddof=0))
    previous_debits = [max(0.0, float(t.get("debit") or 0)) for t in historical if float(t.get("debit") or 0) > 0]
    previous_mean = sum(previous_debits) / len(previous_debits) if previous_debits else None
    normalized = [re.sub(r"[^a-z0-9 ]", " ", str(t.get("normalized_description") or t.get("description") or "").lower()).strip() for t in transactions]

    # Very frequent legitimate merchants should not all be marked as anomalous.
    # Flag only descriptions with at least 8 entries during one calendar month.
    frequent_month = Counter((name, str(tx.get("date") or "")[:7]) for name, tx in zip(normalized, transactions) if name)
    frequent_names = {name for (name, _month), count in frequent_month.items() if count >= 8}

    def key(tx):
        amount, direction = _amount_direction(tx)
        return (str(tx.get("date") or ""), round(amount, 2), direction)

    def ref_matches(tx, other):
        return bool(tx.get("reference") and tx.get("reference") == other.get("reference"))

    current_buckets = defaultdict(list)
    for index, tx in enumerate(transactions):
        current_buckets[key(tx)].append(index)
    historical_buckets = defaultdict(list)
    for tx in historical:
        historical_buckets[key(tx)].append(tx)

    def add(index, reason, method, severity="medium", evidence=None):
        tx = transactions[index]
        flag = {"transaction_id": str(tx.get("_id", index)), "reason": reason, "method": method,
                "severity": severity, "review_status": "pending"}
        if evidence:
            flag["evidence"] = evidence
        flags.append(flag)

    for i, tx in enumerate(transactions):
        debit = current_debits[i]
        if debit > 0 and debit > iqr_cutoff:
            add(i, f"{_transaction_label(tx)} has a debit of INR {debit:,.2f}, above this statement's IQR limit of INR {iqr_cutoff:,.2f}.", "IQR", evidence={"amount": debit, "threshold": float(iqr_cutoff)})
        if len(series) >= 5 and std > 0 and debit > mean + 3 * std:
            add(i, f"{_transaction_label(tx)} has a debit of INR {debit:,.2f}, above the three-standard-deviation limit of INR {mean + 3 * std:,.2f}.", "Z-score", "high", {"amount": debit, "threshold": mean + 3 * std, "mean_debit": mean, "standard_deviation": std})
        if previous_mean and len(previous_debits) >= 5 and debit > previous_mean * 3:
            add(i, f"{_transaction_label(tx)} has a debit of INR {debit:,.2f}, over three times the prior average debit of INR {previous_mean:,.2f}.", "historical_average_deviation", "high", {"amount": debit, "historical_average_debit": previous_mean, "threshold": previous_mean * 3})
        if normalized[i] and normalized[i] in frequent_names:
            month = str(tx.get("date") or "")[:7]
            count = frequent_month.get((normalized[i], month), 0)
            add(i, f"{_transaction_label(tx)} is one of {count} matching descriptions in {month or 'this statement month'}.", "transaction_frequency", "medium", {"merchant": tx.get("description"), "monthly_count": count, "month": month, "threshold": 8})

        amount, direction = _amount_direction(tx)
        candidates = current_buckets[key(tx)]
        duplicate = next((transactions[j] for j in candidates if j < i and (ref_matches(tx, transactions[j]) or _similar(tx.get("description"), transactions[j].get("description")))), None)
        if amount > 0 and duplicate:
            add(i, f"{_transaction_label(tx)} for INR {amount:,.2f} may duplicate an earlier {_transaction_label(duplicate)}.", "date_amount_direction_description_reference", "low", {"amount": amount, "matched_description": duplicate.get("description"), "matched_date": duplicate.get("date"), "matched_reference": duplicate.get("reference")})
        other_matches = historical_buckets.get(key(tx), ())
        historical_match = next((other for other in other_matches if ref_matches(tx, other) or _similar(tx.get("description"), other.get("description"))), None)
        if amount > 0 and historical_match:
            add(i, f"{_transaction_label(tx)} for INR {amount:,.2f} may duplicate a row from another statement ({_transaction_label(historical_match)}).", "cross_statement_duplicate", "low", {"amount": amount, "matched_description": historical_match.get("description"), "matched_date": historical_match.get("date"), "matched_reference": historical_match.get("reference")})
    return flags
