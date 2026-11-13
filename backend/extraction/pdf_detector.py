import fitz


def inspect_pdf(path, min_text_chars=80, image_page_ratio=0.55):
    try:
        doc = fitz.open(path)
        if doc.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")
        pages, text_chars, image_pages = [], 0, 0
        for page in doc:
            text = page.get_text("text") or ""
            text_chars += len(text.strip())
            image_area = sum(fitz.Rect(rect).get_area() for image in page.get_images(full=True) for rect in page.get_image_rects(image[0]))
            ratio = min(1.0, image_area / max(page.rect.get_area(), 1))
            image_pages += ratio >= image_page_ratio
            pages.append({"text": text, "image_ratio": ratio})
        scanned = text_chars < min_text_chars or image_pages / max(len(pages), 1) >= 0.5
        return {"pages": pages, "page_count": len(pages), "type": "scanned" if scanned else "text", "metadata": doc.metadata or {}}
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The uploaded file is not a readable PDF.") from exc
