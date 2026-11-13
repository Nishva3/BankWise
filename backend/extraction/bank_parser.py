import re

from extraction.parsers.axis import AxisParser
from extraction.parsers.hdfc import HDFCParser
from extraction.parsers.icici import ICICIParser
from extraction.parsers.sbi import SBIParser
from extraction.parsers.generic import GenericParser
from extraction.data_cleaner import parse_amount

PARSERS = (SBIParser(), HDFCParser(), ICICIParser(), AxisParser())
DATE_RE = re.compile(r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[- ]+[A-Za-z]{3}[- ]+\d{2,4}|\d{4}-\d{2}-\d{2})\b", re.I)
HEADER_FIELDS = ("date", "particular", "description", "debit", "withdrawal", "credit", "deposit", "balance", "narration", "value dt")


def identify_bank(text):
    header_lines = []
    for line in text.splitlines():
        if DATE_RE.match(line.strip()) or _detect_columns(line):
            break
        header_lines.append(line)
    header = "\n".join(header_lines).lower()
    if re.search(r"\b(?:SBIN)0[A-Z0-9]{6}\b", header): return "SBI"
    if re.search(r"\bHDFC0[A-Z0-9]{6}\b", header): return "HDFC"
    if re.search(r"\bICIC0[A-Z0-9]{6}\b", header): return "ICICI"
    if re.search(r"\bUTIB0[A-Z0-9]{6}\b", header): return "Axis"
    return next((parser.bank_name for parser in PARSERS if parser.identifies(header)), "Unknown")


def parse_pages(pages):
    text = "\n".join(pages)
    bank = identify_bank(text)
    parser = next((p for p in PARSERS if p.bank_name == bank), GenericParser())
    rows, warnings, columns = [], ([] if parser.bank_name != "Unknown" else ["Bank could not be identified; generic parser used."]), None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        detected_columns = _detect_columns(line)
        if detected_columns:
            columns = detected_columns
            continue
        if not DATE_RE.match(line) and any(word in line.lower() for word in HEADER_FIELDS):
            continue
        result = parser.parse_line(line, columns)
        if result:
            rows.append(result)
        elif rows and not DATE_RE.match(line) and not re.search(r"opening balance|closing balance|statement period", line, re.I):
            if not re.search(r"page\s+\d+|continued|total", line, re.I):
                rows[-1]["description"] = (rows[-1]["description"] + " " + line).strip()
    return {"bank_name": parser.bank_name,
            "account_holder": _capture(text, r"(?:account holder|customer name|name)\s*:?\s*([A-Za-z][A-Za-z .]{2,60})"),
            "account_number": _capture(text, r"(?:account\s*(?:number|no\.?))\s*[:#-]?\s*([Xx*\d -]{6,24})"),
            "ifsc": _capture(text, r"\b([A-Z]{4}0[A-Z0-9]{6})\b"),
            "statement_period": _capture(text, r"(?:statement period|period)\s*:?\s*(.{0,80})"),
            "opening_balance": _amount_capture(text, r"opening\s+balance\s*:?\s*((?:\u20b9|INR\s*|Rs\.?\s*)?\(?-?[\d,]+(?:\.\d{2})?\)?)"),
            "closing_balance": _amount_capture(text, r"closing\s+balance\s*:?\s*((?:\u20b9|INR\s*|Rs\.?\s*)?\(?-?[\d,]+(?:\.\d{2})?\)?)"),
            "transactions": rows, "warnings": warnings + (["No transaction rows were recognized."] if not rows else [])}


def _detect_columns(line):
    parts = [part.strip() for part in re.split(r"\s{2,}|\|", line.strip().strip("|"))]
    if len(parts) < 3:
        return None
    mapping = {}
    for i, part in enumerate(parts):
        p = re.sub(r"[^a-z]+", " ", part.lower()).strip()
        if "date" in p and "value" not in p and "date" not in mapping: mapping["date"] = i
        elif "value date" in p or p in ("valuedt", "value dt"): mapping["value_date"] = i
        if any(word in p for word in ("narration", "description", "particular", "remarks")): mapping["description"] = i
        if any(word in p for word in ("withdrawal", "debit", "dr amt", "debit amt")): mapping["debit"] = i
        if any(word in p for word in ("deposit", "credit", "cr amt", "credit amt")): mapping["credit"] = i
        if "balance" in p: mapping["balance"] = i
        if any(word in p for word in ("reference", "chq no", "cheque no", "utr", "transaction id")) or ("chq" in p and "ref" in p): mapping["reference"] = i
    if "date" in mapping and "description" in mapping and "balance" in mapping and ("debit" in mapping or "credit" in mapping):
        mapping["_count"] = len(parts)
        return mapping
    return None


def _capture(text, pattern):
    match = re.search(pattern, text, re.I)
    return match.group(1).strip() if match else None


def _amount_capture(text, pattern):
    value = _capture(text, pattern)
    return parse_amount(value) if value else None
