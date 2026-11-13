import os
from pathlib import Path

from dotenv import load_dotenv


# Load the project-level .env when the backend is started from any working
# directory. Existing process environment variables keep precedence.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60")) * 60
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bankwise")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MODEL_DIR = os.getenv("MODEL_DIR", "models")
    OCR_LANG = os.getenv("OCR_LANG", "eng")
    OCR_DPI = int(os.getenv("OCR_DPI", "250"))
    OCR_MIN_CONFIDENCE = float(os.getenv("OCR_MIN_CONFIDENCE", "55"))
    TESSERACT_CMD = os.getenv("TESSERACT_CMD") or None
    MIN_TEXT_CHARS = int(os.getenv("MIN_TEXT_CHARS", "80"))
    IMAGE_PAGE_RATIO = float(os.getenv("IMAGE_PAGE_RATIO", "0.55"))
    CLASSIFICATION_THRESHOLD = float(os.getenv("CLASSIFICATION_THRESHOLD", "0.55"))
    BALANCE_TOLERANCE = float(os.getenv("BALANCE_TOLERANCE", "1.00"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024
    ADMIN_EMAILS = [x.strip().lower() for x in os.getenv("ADMIN_EMAILS", "").split(",") if x.strip()]
    MIN_FEEDBACK_FOR_RETRAIN = int(os.getenv("MIN_FEEDBACK_FOR_RETRAIN", "5"))
    MIN_MODEL_F1 = float(os.getenv("MIN_MODEL_F1", "0.50"))

