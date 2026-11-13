import fitz
import pdfplumber


def extract_text(path):
    """Choose the PDF text layout that yields the most transaction rows."""
    with fitz.open(path) as doc:
        primary = [page.get_text("text") or "" for page in doc]
    candidates = [primary]
    try:
        with pdfplumber.open(path) as pdf:
            alternate = [page.extract_text(layout=False) or "" for page in pdf.pages]
            if len(alternate) == len(primary):
                candidates.append(alternate)
                candidates.append([
                    alt if len(alt) > len(base) else base
                    for base, alt in zip(primary, alternate)
                ])
    except Exception:
        pass

    # Column-based statements can be extracted as one vertical text block per
    # column. Text length alone selects that unusable layout in some PDFs.
    # Score complete document candidates by rows recognized by the real parser.
    from extraction.bank_parser import parse_pages
    scored = []
    for pages in candidates:
        try:
            row_count = len(parse_pages(pages)["transactions"])
        except Exception:
            row_count = 0
        scored.append((row_count, sum(map(len, pages)), pages))
    return max(scored, key=lambda item: (item[0], item[1]))[2]
