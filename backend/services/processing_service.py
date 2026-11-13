from extraction.pdf_detector import inspect_pdf
from extraction.text_extractor import extract_text
from extraction.ocr_extractor import extract_ocr
from extraction.bank_parser import parse_pages
from extraction.data_cleaner import clean_transaction, reconcile
from classification.hybrid import classify


def process_statement(path, classifier, config, db=None):
    get = config.get if hasattr(config, "get") else lambda key, default=None: getattr(config, key, default)
    detection = inspect_pdf(path, get("MIN_TEXT_CHARS", 80), get("IMAGE_PAGE_RATIO", 0.55))
    ocr_warnings = []
    if detection["type"] == "scanned": pages, ocr_warnings = extract_ocr(path, get("OCR_DPI", 250), get("OCR_LANG", "eng"), get("TESSERACT_CMD"), get("OCR_MIN_CONFIDENCE", 55.0))
    else: pages = extract_text(path)
    parsed = parse_pages(pages)
    if not parsed["transactions"]:
        raise ValueError("No transactions could be read from this PDF. Try a text-based statement with a visible date, description, debit or credit, and balance for each row.")
    rows = [clean_transaction(row) for row in parsed["transactions"]]
    custom_rules = list(db.classification_rules.find({"enabled": True}).sort("priority", -1)) if db is not None else []
    for row in rows:
        row.update(classify(row.get("normalized_description", ""), classifier, db, custom_rules))
        low_ocr_confidence = any("OCR confidence is low" in warning for warning in ocr_warnings)
        if row.get("validation_warnings") or low_ocr_confidence:
            if low_ocr_confidence: row.setdefault("validation_warnings", []).append("Low OCR confidence; verify extracted transaction fields.")
            row["review_required"] = True
            row["review_status"] = "pending"
    reconciliation = reconcile(parsed.get("opening_balance"), rows, parsed.get("closing_balance"), get("BALANCE_TOLERANCE", 1.0))
    warnings = parsed["warnings"] + ocr_warnings
    if reconciliation["reconciled"] is False: warnings.append("Opening-to-closing balance reconciliation failed; extracted values were not changed.")
    return {"detection": {"type": detection["type"], "page_count": detection["page_count"], "metadata": detection["metadata"]},
            "parsed": parsed, "transactions": rows, "validation": {"balance_reconciliation": reconciliation},
            "warnings": warnings}
