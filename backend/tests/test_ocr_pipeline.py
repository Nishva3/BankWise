import shutil
import io

import fitz
import pytest
from PIL import Image, ImageDraw, ImageFont

from extraction.ocr_extractor import extract_ocr, preprocess
from extraction.pdf_detector import inspect_pdf


def test_multipage_text_pdf_detection(tmp_path):
    path = tmp_path / "multipage.pdf"
    doc = fitz.open()
    for i in range(2):
        page = doc.new_page(); page.insert_text((40, 50), f"Bank statement page {i+1}. Account transaction information and balances." * 2)
    doc.save(path); doc.close()
    assert inspect_pdf(path)["page_count"] == 2
    assert inspect_pdf(path)["type"] == "text"


def test_password_protected_pdf_is_rejected(tmp_path):
    path = tmp_path / "encrypted.pdf"
    doc = fitz.open(); doc.new_page(); doc.save(path, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="ownerpass", user_pw="userpass"); doc.close()
    with pytest.raises(ValueError, match="Password-protected"):
        inspect_pdf(path)


def _tesseract_command():
    return shutil.which("tesseract") or (r"C:\Program Files\Tesseract-OCR\tesseract.exe" if __import__("os").path.isfile(r"C:\Program Files\Tesseract-OCR\tesseract.exe") else None)


@pytest.mark.skipif(_tesseract_command() is None, reason="Tesseract executable is not installed locally")
def test_scanned_pdf_preprocessing_and_ocr(tmp_path):
    image = Image.new("RGB", (1800, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 60), "BANK STATEMENT 01/04/2025 UPI SWIGGY 450.00 Dr", fill="black")
    png = tmp_path / "scan.png"; image.save(png)
    path = tmp_path / "scanned.pdf"
    doc = fitz.open(); page = doc.new_page(width=900, height=250); page.insert_image(page.rect, filename=str(png)); doc.save(path); doc.close()
    assert inspect_pdf(path)["type"] == "scanned"
    pages, warnings = extract_ocr(path, tesseract_cmd=_tesseract_command())
    assert len(pages) == 1 and pages[0].strip()
    assert isinstance(warnings, list)


@pytest.mark.skipif(_tesseract_command() is None, reason="Tesseract executable is not installed locally")
def test_poor_quality_scan_retains_review_warning(tmp_path):
    image = Image.new("RGB", (1600, 900), "white")
    path = tmp_path / "blank-scan.pdf"
    image_bytes = io.BytesIO(); image.save(image_bytes, format="JPEG")
    doc = fitz.open(); page = doc.new_page(width=800, height=450); page.insert_image(page.rect, stream=image_bytes.getvalue()); doc.save(path); doc.close()
    pages, warnings = extract_ocr(path, tesseract_cmd=_tesseract_command())
    assert pages == [""]
    assert warnings and "manual review" in warnings[0].lower()


@pytest.mark.skipif(_tesseract_command() is None, reason="Tesseract executable is not installed locally")
def test_distributed_scanned_statement_extracts_transaction():
    from pathlib import Path
    from extraction.bank_parser import parse_pages
    from extraction.data_cleaner import clean_transaction, reconcile
    path = Path(__file__).resolve().parents[2] / "dataset" / "statements" / "scanned_synthetic_sample.pdf"
    pages, warnings = extract_ocr(path, tesseract_cmd=_tesseract_command())
    parsed = parse_pages(pages)
    rows = [clean_transaction(row) for row in parsed["transactions"]]
    assert parsed["bank_name"] == "HDFC"
    assert len(rows) == 1
    assert "SWIGGY" in rows[0]["description"].upper()
    assert reconcile(parsed["opening_balance"], rows, parsed["closing_balance"])["reconciled"] is True


def test_ocr_preprocessing_returns_grayscale_binary_image():
    image = Image.new("RGB", (80, 40), "white")
    processed = preprocess(image)
    assert processed.mode == "L"
