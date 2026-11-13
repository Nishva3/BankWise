import json
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

ROOT = Path.cwd()
WORK = ROOT / "tmp" / "bankwise_sample_2"
OUTPUT = ROOT / "outputs" / "bankwise_sample_2_20261113" / "bankwise_sample_dataset_2.pdf"
data = json.loads((WORK / "transactions.json").read_text(encoding="utf-8"))
rows = data["rows"]
PAGE_W, PAGE_H = letter
LEFT, RIGHT = 38, PAGE_W - 38
LINE_H = 13
ROWS_PER_PAGE = 46
pages = (len(rows) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
doc = canvas.Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
doc.setTitle("BankWise Synthetic Test Statement 2")
doc.setAuthor("BankWise synthetic test data generator")

for page_no in range(pages):
    batch = rows[page_no * ROWS_PER_PAGE:(page_no + 1) * ROWS_PER_PAGE]
    y = PAGE_H - 42
    doc.setFont("Helvetica-Bold", 12)
    doc.drawString(LEFT, y, "BANKWISE - SYNTHETIC TEST STATEMENT")
    y -= 17
    doc.setFont("Helvetica", 8)
    doc.drawString(LEFT, y, "Synthetic test data - not a bank-issued statement")
    y -= 14
    doc.drawString(LEFT, y, "Account Holder: TEST USER    Account Number: XXXXXX1234 (dummy)")
    y -= 12
    doc.drawString(LEFT, y, "Bank format: HDFC-style    IFSC: HDFC0000001 (dummy)")
    y -= 12
    doc.drawString(LEFT, y, "Statement Period: 01/08/2026 - 30/10/2026")
    y -= 12
    doc.drawString(LEFT, y, f"Opening Balance: INR {data['openingBalance']:,.2f}    Closing Balance: INR {data['closingBalance']:,.2f}")
    y -= 19
    doc.setFont("Courier-Bold", 7.2)
    header = "Date        Description                         Debit       Credit      Balance"
    doc.drawString(LEFT, y, header)
    y -= 4
    doc.setStrokeColorRGB(0.10, 0.32, 0.25)
    doc.line(LEFT, y, RIGHT, y)
    y -= 12
    doc.setFont("Courier", 6.8)
    for row in batch:
        date = "/".join(reversed(row["date"].split("-")))
        description = row["description"][:34]
        line = f"{date:<10}  {description:<34}  {row['debit']:>10,.2f}  {row['credit']:>10,.2f}  {row['balance']:>11,.2f}"
        if stringWidth(line, "Courier", 6.8) > RIGHT - LEFT:
            raise ValueError(f"Statement row exceeds page width: {line}")
        doc.drawString(LEFT, y, line)
        y -= LINE_H
    doc.setFont("Helvetica", 7)
    doc.setFillColorRGB(0.32, 0.35, 0.34)
    doc.drawRightString(RIGHT, 22, f"Page {page_no + 1} of {pages}")
    doc.showPage()

doc.save()
print(f"Created {OUTPUT} with {len(rows)} rows on {pages} pages")
