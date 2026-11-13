from services import processing_service


class Model:
    threshold = .5
    def predict(self, _description): return {"category": "Food & Dining", "method": "ml", "confidence": .95, "review_required": False}


def test_low_ocr_confidence_forces_manual_review(monkeypatch):
    monkeypatch.setattr(processing_service, "inspect_pdf", lambda *_: {"type": "scanned", "page_count": 1, "metadata": {}})
    monkeypatch.setattr(processing_service, "extract_ocr", lambda *_args: (["HDFC Bank\n01/04/2025 UNKNOWN PURCHASE 10.00 Dr 90.00"], ["Page 1: OCR confidence is low; manual review recommended."]))
    config = {"MIN_TEXT_CHARS": 80, "IMAGE_PAGE_RATIO": .55, "OCR_DPI": 250, "OCR_LANG": "eng", "TESSERACT_CMD": None, "OCR_MIN_CONFIDENCE": 55, "BALANCE_TOLERANCE": 1}
    result = processing_service.process_statement("not-opened-by-monkeypatch.pdf", Model(), config)
    row = result["transactions"][0]
    assert row["review_required"] is True
    assert row["review_status"] == "pending"
    assert any("Low OCR confidence" in warning for warning in row["validation_warnings"])
