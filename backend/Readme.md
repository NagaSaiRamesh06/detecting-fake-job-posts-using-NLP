# JobCheck - Backend Service

This is the backend API and server-side rendering service for **JobCheck**, a web application designed to detect fake job postings using NLP, Machine Learning, and OCR.

## ✨ Features

- **Flask Application**: Modular structure serving Jinja2 templates and providing a JSON API for decoupled clients.
- **AI Prediction Pipeline**: Text cleaning, TF-IDF Vectorization, and classification using a Linear SVM model.
- **Image Scanning (OCR)**: Extracts text from images of job ads using OpenCV and Tesseract OCR.
- **JWT & Role Authentication**: Dual session-based auth for templates and stateless JWT auth for the API.
- **Database Logs**: SQLite integration for user registration, admin management, and audit logging of predictions.

## 📂 Project Structure

```
backend/
├── App/                  # Core application package
│   ├── app.py            # Flask app factory and initialization
│   ├── config.py         # Application configuration & path constants
│   ├── database.py       # Database connection setup & migrations
│   ├── data_processor.py # Text preprocessing & dataset cleaning
│   ├── routes.py         # Flask routes, prediction engine, & API endpoints
│   └── users.db          # Local SQLite database (Git ignored)
├── Dataset/              # Dataset directory
│   └── fake_job_postings.csv # Training dataset
├── Model/                # Trained models & metrics
│   ├── best_model.pkl    # Trained Linear SVM classifier
│   ├── tfidf.pkl         # Fitted TF-IDF Vectorizer
│   └── model_metadata.json # Best model metrics
├── Static/               # Static assets (CSS/JS)
│   ├── auth.js           # Client-side form handlers & UI scripts
│   ├── style.css         # Baseline style definitions
│   └── styles.css        # Premium Glassmorphism styling rules
├── Templates/            # Jinja2 HTML Templates
│   ├── base.html         # Global layout and sidebar
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── predict.html      # Job text analysis & image upload
│   ├── dashboard.html    # User statistics and scan history
│   ├── admin.html        # System analytics & user management
│   └── profile.html      # User profile page
├── Uploads/              # Temp directory for OCR files (Git ignored)
├── tests/                # Test suite
│   ├── __init__.py       # Package initializer
│   ├── test_jwt.py       # JWT authentication and API tests
│   ├── test_ocr.py       # Self-contained Tesseract OCR tests
│   └── test_prediction.py # ML model prediction tests
├── .env.example          # Environment variables configuration template
├── Dockerfile            # Container definition
├── Procfile              # Deployment commands (Heroku/Render)
├── render.yaml           # Render deployment configuration
├── requirements.txt      # Python dependencies
└── wsgi.py               # WSGI application entry point
```

## 🛠️ Installation & Local Setup

### 1. Prerequisites
- Python 3.9+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed on your system. 
  *On Windows, make sure it is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`.*

### 2. Configure Environment Variables
Copy `.env.example` to a new file named `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your custom keys (e.g. `SECRET_KEY`, `JWT_SECRET_KEY`, etc.).

### 3. Initialize Virtual Environment & Install Dependencies
From the `backend/` directory:
```bash
python -m venv .venv
# Activate:
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Mac/Linux

pip install -r requirements.txt
```

### 4. Run Database Migrations
Initialize the SQLite database schema and generate the default admin user:
```bash
python migrate.py
```
*Default admin credentials: Username `admin`, Password `admin`.*

## ▶️ Running the Server

Start the Flask development server:
```bash
python -m App.app
```
The server will start running on **`http://127.0.0.1:5000`**.

## 🧪 Running Unit Tests

Run the unit test suite containing authentication, OCR processing, and prediction tests:
```bash
python -m unittest discover -s tests
```
