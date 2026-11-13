import re

DEFAULT_RULES = [
    ("Food & Dining", [r"zomato", r"swiggy", r"restaurant", r"foodpanda"]),
    ("Groceries", [r"bigbasket", r"blinkit", r"grocery", r"dmart"]),
    ("Shopping", [r"amazon", r"flipkart", r"myntra"]),
    ("Transportation", [r"uber", r"ola", r"rapido", r"metro"]),
    ("Entertainment", [r"netflix", r"spotify", r"bookmyshow"]),
    ("Healthcare", [r"hospital", r"pharmacy", r"apollo"]),
    ("Education", [r"school", r"university", r"tuition"]),
    ("Utilities", [r"electricity", r"water bill", r"airtel", r"jio"]),
    ("Housing & Rent", [r"rent", r"maintenance"]), ("Travel", [r"air india", r"indigo", r"makemytrip"]),
    ("Insurance", [r"insurance", r"premium"]), ("Salary & Income", [r"salary", r"payroll"]),
    ("Investments", [r"mutual fund", r"sip", r"zerodha", r"investment"]),
    ("ATM & Cash Withdrawal", [r"atm", r"cash withdrawal"]), ("Bank Charges", [r"bank charge", r"service fee", r"sms charge"]),
    ("Loan & EMI", [r"emi", r"loan repayment"]), ("Transfers", [r"neft", r"imps", r"upi", r"rtgs", r"transfer"])]

CATEGORIES = tuple(category for category, _ in DEFAULT_RULES) + ("Other / Uncategorized",)


def classify_rule(description, db=None, rules=None):
    if rules is None:
        rules = db.classification_rules.find({"enabled": True}).sort("priority", -1) if db is not None else []
    candidates = [(r["category"], r["pattern"]) for r in rules]
    candidates += [(cat, pattern) for cat, patterns in DEFAULT_RULES for pattern in patterns]
    for category, pattern in candidates:
        try:
            if re.search(pattern, description or "", re.I):
                return {"category": category, "method": "rule", "confidence": 1.0}
        except re.error: continue
    return None
