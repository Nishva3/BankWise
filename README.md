# BankWise backend

Flask and MongoDB backend for PDF statement ingestion, extraction, transaction classification, analytics, anomaly review and exports, connected to the Stitch-generated BankWise frontend. No LLM or generative AI is used.

## Run locally

Install Tesseract OCR and MongoDB, create a virtual environment, run `pip install -r requirements.txt`, copy `.env.example` to `.env`, and replace both secrets with long random values. The example uses local MongoDB at `mongodb://localhost:27017/bankwise`. On Windows, set `TESSERACT_CMD` to the full path of `tesseract.exe` if it is not on PATH. From `backend/`, run `python app.py`; the API listens at `http://localhost:5000`. Run tests from the project root with `python -m pytest backend/tests`.

Set `MODEL_DIR` to a writable directory. From `backend/`, train the baseline classifiers with `python -m classification.train_model`. The script fits and saves a TF-IDF plus Logistic Regression model at `models/classifier.joblib`, and writes `models/evaluation.json` with held-out accuracy, weighted F1, per-class precision/recall/F1 and confusion matrix for both Logistic Regression and Multinomial Naive Bayes. The checked-in model was trained on 288 deterministic synthetic rows across 18 categories. Its measured held-out scores are reproducible for this corpus, but do not estimate real-world bank transaction performance. Rule matches take precedence over ML predictions.

## API workflow

1. `POST /api/auth/register` with `{ "email": "you@example.com", "password": "a-long-password" }`.
2. `POST /api/auth/login`; send the returned token as `Authorization: Bearer <token>`.
3. `POST /api/statements/upload` using multipart form data with the `file` field.
4. `POST /api/statements/{id}/process`, then poll `GET /api/statements/{id}/status`.
5. Query `/api/transactions?page=1&limit=25`, correct a category via `PUT /api/transactions/{id}` with `{ "category": "Groceries" }`, and export using `/api/export/csv` or `/api/export/excel`.

Login returns a JSON token response similar to:

```json
{"access_token":"<jwt>","token_type":"Bearer","expires_in":3600}
```

Upload returns `{ "statement_id": "<id>", "status": "uploaded" }`; completed processing returns `{ "statement_id": "<id>", "status": "completed", "transaction_count": 24, "warnings": [] }`. Transaction list responses contain `items`, `page`, `limit`, and `total`. Transaction filters include `category`, `statement_id`, `date_from`, `date_to`, and `search`. Every `/api/*` endpoint except registration and login requires the bearer token. Statement and transaction IDs are checked against the authenticated owner.

Example upload:

```bash
curl -H "Authorization: Bearer $TOKEN" -F "file=@statement.pdf" http://localhost:5000/api/statements/upload
```

Regular user data queries are owner-scoped; admin-only feedback review and model operations are role-checked. Ordinary statement responses preserve only the masked last four account digits. Uploads are stored under `UPLOAD_DIR` with random server-side names and a configurable request size cap. Logs do not include statement text or account numbers. Production deployments must set secrets, restrict CORS, and terminate TLS at a trusted proxy.

## Run the Stitch frontend

1. Start MongoDB and the Flask API using the setup above. The API listens at `http://localhost:5000`.
2. From the project root, start the static frontend server with `python -m http.server 5173 --directory frontend`.
3. Open `http://localhost:5173/`. Register or sign in; the frontend stores the bearer token in browser local storage and sends it on authenticated API requests.
4. The frontend connects to `http://localhost:5000` by default. If you use another frontend port or host, add that exact origin to `CORS_ORIGINS` in `.env` and restart the backend.

The Stitch pages use Tailwind and icon fonts from their CDNs, so an internet connection is needed for those visual assets. Their workspace views are rendered from the signed-in account through the Flask API for authentication, statement upload and processing, transactions and category corrections, analytics, anomaly review, and CSV/Excel downloads. Upload unlocked PDF files; password-protected PDFs are not supported. Users can update their name, phone, institution, and city from the profile dialog. Password reset and password changes are not implemented. Workspace screens replace prototype rows with account data after sign-in; appearance preferences are stored in the browser.

## Architecture and current limits

- `backend/extraction`: text and OCR pipelines, scanned/text detection, four bank identification adapters, header-mapped and generic table-row parsing, cleaning and reconciliation helpers.
- `backend/classification`: configurable MongoDB regex rules, deterministic merchant rules, TF-IDF/Logistic Regression inference and evaluation.
- `backend/analytics`: cash-flow, category, month-over-month and recurring-payment insights. Analytics separates explicitly recognized income, refunds, other credits, gross debits and net expenses; classifier accuracy/F1 are holdout model-evaluation metrics and are not a statement-level accuracy claim. Anomaly flags use IQR, z-score, historical-average, frequency and duplicate checks.
- `backend/routes`: authenticated Flask endpoints, ownership checks, feedback capture and exports.
- MongoDB collections are indexed on owner, statement, and creation/query fields.

Synthetic statement fixtures are provided in `dataset/statements/`: separate two-page text PDFs for SBI, HDFC, ICICI, and Axis plus a scanned HDFC-style sample. Regenerate them with `python dataset/statements/build_samples.py`. They contain only dummy test data and are not bank-issued documents.

SBI, HDFC, ICICI and Axis parser adapters are covered by synthetic generated text-PDF fixtures, not real bank-issued samples. Row extraction remains heuristic and flags uncertain rows. Real layout validation and held-out bank statement fixtures are required before trusting extracted values. OCR warnings and row warnings are retained, but extraction quality depends on scan quality and Tesseract language installation. The synthetic transaction corpus is not a credible benchmark. Anomaly checks flag unusual activity for review and do not label activity as fraud.

Corrections are stored as unapproved feedback. Set `ADMIN_EMAILS` before registering operator accounts; those accounts can approve a correction with `PUT /api/classification/feedback/{feedback_id}/approve` and call `POST /api/classification/retrain`. Retraining requires `MIN_FEEDBACK_FOR_RETRAIN` approved corrections and promotes only when candidate weighted F1 meets `MIN_MODEL_F1` and does not regress against the currently loaded model on the same held-out split. Rejected candidates leave the current model in place. Processing currently runs synchronously in the request; use a task queue before handling large or high-volume statements.

## Configuration

See `.env.example`. `MIN_TEXT_CHARS`, `IMAGE_PAGE_RATIO`, OCR DPI/language and `TESSERACT_CMD`, amount tolerance, classification confidence threshold, feedback approval count and minimum promotion F1 are configurable. Set `TESSERACT_CMD` when Tesseract is installed outside `PATH`. PDFs are rejected if encrypted or unreadable during processing. Uploads accept only `.pdf` filenames and PDF media types and obey Flask's max content length.

## Tests

Run `python -m pytest backend/tests`. Tests cover cleaning, synthetic PDFs for four bank headers, unknown bank fallback, corrupt/encrypted/multipage PDF handling, OCR preprocessing and scanned-page recognition, ownership scoping, authentication, classification evaluation, feedback retraining, anomalies, exports, and a live MongoDB upload-to-export integration flow. Statement fixtures remain synthetic; the live integration test uses a temporary uniquely named database and removes it at teardown.
