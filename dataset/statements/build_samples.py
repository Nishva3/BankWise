"""Create synthetic, non-bank-issued statement PDFs for parser and OCR tests."""
from pathlib import Path
import io

import fitz
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
ROWS = [
    ("01/04/2025", "01/04/2025", "UPI/DR/SWIGGY", "UPI123450001", "450.00", "0.00", "550.00"),
    ("03/04/2025", "03/04/2025", "SALARY CREDIT", "NEFT12345002", "0.00", "45000.00", "45550.00"),
    ("05/04/2025", "05/04/2025", "CARD/DR/PHARMACY", "POS12345003", "1250.00", "0.00", "44300.00"),
    ("06/04/2025", "06/04/2025", "NEFT/CR/REFUND", "NEFT12345004", "0.00", "750.00", "45050.00"),
]
BANK_LAYOUTS = {
    "sbi": {"name": "State Bank of India", "ifsc": "SBIN0000001", "header": ("Txn Date", "Value Date", "Description", "Debit", "Credit", "Balance"), "indices": (0, 1, 2, 4, 5, 6)},
    "hdfc": {"name": "HDFC Bank", "ifsc": "HDFC0000001", "header": ("Date", "Narration", "Chq./Ref.No.", "ValueDt", "WithdrawalAmt.", "DepositAmt.", "ClosingBalance"), "indices": (0, 2, 3, 1, 4, 5, 6)},
    "icici": {"name": "ICICI Bank", "ifsc": "ICIC0000001", "header": ("Transaction Date", "Particulars", "Transaction ID", "Debit", "Credit", "Balance"), "indices": (0, 2, 3, 4, 5, 6)},
    "axis": {"name": "Axis Bank", "ifsc": "UTIB0000001", "header": ("Tran Date", "Particulars", "Reference No", "Value Date", "Dr Amount", "Cr Amount", "Balance"), "indices": (0, 2, 3, 1, 4, 5, 6)},
}


def _text_pdf(bank_key, layout):
    path = OUT / f"{bank_key}_synthetic_sample.pdf"
    doc = fitz.open()
    for page_no in range(2):
        page = doc.new_page(width=595, height=842)
        lines = [
            "SYNTHETIC TEST DATA - NOT A BANK ISSUED STATEMENT",
            layout["name"],
            "Account Holder: TEST USER",
            "Account Number: XXXXXX1234",
            f"IFSC: {layout['ifsc']}",
            "Statement Period: 01/04/2025 - 30/04/2025",
            "Opening Balance: INR 1,000.00",
            "Closing Balance: INR 45,050.00",
        ]
        if page_no == 0:
            lines.extend(["", "    ".join(layout["header"])])
        else:
            lines.extend(["", "    ".join(layout["header"])])
        for row in ROWS[page_no * 2:(page_no + 1) * 2]:
            lines.append("    ".join(row[i] for i in layout["indices"]))
        page.insert_textbox(fitz.Rect(40, 35, 560, 800), "\n".join(lines), fontsize=9, lineheight=1.55, fontname="cour")
    doc.set_metadata({"title": f"Synthetic {layout['name']} parser sample", "author": "BankWise test-data generator"})
    doc.save(path); doc.close()
    return path


def _scanned_pdf():
    path = OUT / "scanned_synthetic_sample.pdf"
    image = Image.new("RGB", (1800, 1200), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 48) if font_path.exists() else ImageFont.load_default()
    lines = ["SYNTHETIC TEST DATA - NOT A BANK ISSUED STATEMENT", "HDFC BANK", "Account Holder: TEST USER", "Account Number: XXXXXX1234", "Statement Period: 01/04/2025 - 30/04/2025", "Opening Balance: INR 1,000.00", "Closing Balance: INR 550.00", "Date       Description                  Debit       Credit       Balance", "01/04/2025 UPI/DR/SWIGGY               450.00      0.00         550.00"]
    y = 55
    for line in lines:
        draw.text((60, y), line, fill="black", font=font); y += 120
    data = io.BytesIO(); image.save(data, format="PNG")
    doc = fitz.open(); page = doc.new_page(width=595, height=842); page.insert_image(page.rect, stream=data.getvalue())
    doc.set_metadata({"title": "Synthetic scanned statement OCR sample", "author": "BankWise test-data generator"})
    doc.save(path); doc.close()
    return path


if __name__ == "__main__":
    files = [_text_pdf(key, layout) for key, layout in BANK_LAYOUTS.items()]
    files.append(_scanned_pdf())
    for file in files: print(file)
