import fitz
import cv2
import numpy as np
import pytesseract
from PIL import Image


def preprocess(image, deskew=True):
    gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    if deskew:
        coords = np.column_stack(np.where(binary < 255))
        if len(coords) > 20:
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            if abs(angle) < 12 and abs(angle) > 0.2:
                h, w = binary.shape
                m = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                binary = cv2.warpAffine(binary, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(binary)


def extract_ocr(path, dpi=250, lang="eng", tesseract_cmd=None, min_confidence=55.0):
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    pages, warnings = [], []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            processed = preprocess(image)
            text = pytesseract.image_to_string(processed, lang=lang, config="--psm 6")
            pages.append(text)
            if len(text.strip()) < 30:
                warnings.append(f"Page {index + 1}: OCR returned very little text; manual review recommended.")
            else:
                data = pytesseract.image_to_data(processed, lang=lang, config="--psm 6", output_type=pytesseract.Output.DICT)
                confidences = [float(value) for value in data.get("conf", []) if str(value).strip() not in ("", "-1") and float(value) >= 0]
                low_ratio = (sum(value < min_confidence for value in confidences) / len(confidences)) if confidences else 0
                if confidences and (sum(confidences) / len(confidences) < min_confidence or low_ratio >= .35):
                    average = sum(confidences) / len(confidences)
                    warnings.append(f"Page {index + 1}: OCR confidence is low (mean {average:.1f}, low-confidence token ratio {low_ratio:.2f}); manual review recommended.")
    return pages, warnings
