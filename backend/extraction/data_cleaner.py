import re
from datetime import datetime

DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y", "%d %b %Y", "%d %b %y", "%d-%b-%Y", "%d-%b-%y", "%Y/%m/%d")


def parse_amount(value):
    if value in (None, "", "-"): return 0.0
    if isinstance(value, (int, float)): return float(value)
    s = re.sub(r"^(?:₹|INR\s*|Rs\.?\s*)", "", str(value).strip(), flags=re.I)
    s = s.replace(",", "").replace("₹", "").replace("INR", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[^\d.+-]", "", s)
    if not s: return 0.0
    result = float(s)
    return -abs(result) if neg else result


def normalize_date(value):
    if not value: return None
    for fmt in DATE_FORMATS:
        try: return datetime.strptime(str(value).strip(), fmt).date().isoformat()
        except ValueError: continue
    return None


def clean_transaction(row):
    out = dict(row)
    out["original_description"] = row.get("description", "")
    out["description"] = re.sub(r"\s+", " ", str(row.get("description", ""))).strip()
    out["normalized_description"] = re.sub(r"[^a-z0-9 ]", " ", out["description"].lower()).strip()
    out["date"] = normalize_date(row.get("date"))
    out["value_date"] = normalize_date(row.get("value_date"))
    for key in ("debit", "credit", "balance"):
        out[key] = parse_amount(row.get(key)) if row.get(key) is not None else None
    out["validation_warnings"] = list(row.get("warnings", []))
    if not out["date"]: out["validation_warnings"].append("Transaction date could not be normalized.")
    if not out["description"]: out["validation_warnings"].append("Transaction description is empty.")
    return out


def reconcile(opening, transactions, closing, tolerance=1.0):
    if opening is None or closing is None:
        return {"reconciled": None, "expected_closing": None, "reported_closing": closing,
                "difference": None, "tolerance": tolerance, "warning": "Opening or closing balance is unavailable."}
    expected = parse_amount(opening) + sum((t.get("credit") or 0) - (t.get("debit") or 0) for t in transactions)
    difference = parse_amount(closing) - expected
    return {"reconciled": abs(difference) <= tolerance, "expected_closing": round(expected, 2), "reported_closing": parse_amount(closing), "difference": round(difference, 2), "tolerance": tolerance}
