# BankWise – AI-Powered Personal Finance Management System

BankWise is an intelligent personal finance management platform designed to simplify financial tracking and help users understand their spending habits. It processes bank statements, extracts transaction data, automatically categorizes expenses, identifies unusual transactions, and generates meaningful financial insights through an interactive dashboard.

## Key Features

- **Bank Statement Processing:** Upload and process PDF bank statements.
- **Transaction Extraction:** Extract transaction dates, descriptions, debit amounts, credit amounts, and balances.
- **Automatic Categorization:** Classify transactions into meaningful financial categories using machine learning.
- **Financial Analytics:** View income, expenses, spending patterns, and cash flow.
- **Anomaly Detection:** Identify unusual or potentially suspicious transactions.
- **Transaction Management:** Review and manage extracted financial records.
- **Data Visualization:** Understand financial activity through interactive charts and summaries.
- **Secure Authentication:** User registration and login functionality.

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Tailwind CSS

### Backend
- Python
- Flask
- REST APIs

### Database
- MongoDB

### AI / Machine Learning
- Scikit-learn
- Pandas
- NumPy

### Document Processing
- PyMuPDF
- pdfplumber
- Tesseract OCR

### Tools
- Git
- GitHub
- Postman
- Docker

## Project Architecture

The application follows a frontend-backend architecture:

1. The frontend provides the user interface for authentication, statement uploads, transaction management, and financial analytics.
2. The Flask backend handles API requests, authentication, document processing, transaction extraction, and machine learning operations.
3. MongoDB stores user information and financial transaction records.
4. The machine learning component assists with transaction categorization and financial analysis.

## Project Structure

```text
BankWise/
├── backend/
│   ├── routes/
│   ├── analytics/
│   ├── classification/
│   ├── extraction/
│   └── app.py
├── frontend/
│   ├── index.html
│   └── app.js
├── models/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

*The structure above is illustrative; refer to the actual repository files for the complete implementation.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/BankWise.git
cd BankWise
```

### 2. Set Up the Python Environment

```bash
python -m venv venv
```

Activate it:

Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file using `.env.example` and configure the required environment variables, including MongoDB connection details and application secrets.

### 5. Start the Backend

```bash
cd backend
python app.py
```

### 6. Start the Frontend

Open another terminal:

```bash
python -m http.server 5173 --directory frontend
```

Open `http://localhost:5173` in your browser.

## Future Enhancements

- Advanced spending predictions.
- Personalized budgeting recommendations.
- Recurring payment detection.
- Multi-bank statement support.
- Enhanced fraud and anomaly detection.
- Financial goal tracking.

## Disclaimer

BankWise is an educational and analytical project. Its outputs are intended for informational purposes and should not be treated as professional financial advice.

---

**Developed by:** Nishva Shah
