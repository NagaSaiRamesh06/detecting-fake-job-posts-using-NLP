# JobCheck – Detecting Fake Job Posts Using NLP

JobCheck is an NLP and Machine Learning based web application designed to analyze job postings and identify potentially fraudulent or fake job advertisements. The system combines text analysis, machine learning classification, OCR-based image analysis, secure authentication, and user/admin functionality.

---

## 🎓 Internship Context

This project was developed as part of the **Infosys Springboard Virtual Internship**. The objective of the internship was to apply academic concepts and construct a production-ready application implementing:
- **Python & Web Development**: Flask API, Routing, HTML/CSS Templates, and session management.
- **Natural Language Processing (NLP)**: Text normalization, cleaning, tokenization, and stop-word filtering.
- **Machine Learning**: TF-IDF vectorization, feature extraction, classifier training, and performance evaluation.
- **Image Processing & OCR**: Computer Vision transformations and Optical Character Recognition.
- **Database & Security**: Relational schemas, secure password hashing, and token-based API authentication.

---

## 🎯 Project Objective

The primary objective of JobCheck is to provide an intelligent and user-friendly platform that assists job seekers in identifying potentially fraudulent job postings using NLP and Machine Learning. By automating the auditing of job postings, the system reduces the risk of identity theft, advance-fee scams, and general recruitment fraud.

---

## 📖 Project Overview

Employment scams have surged with the growth of remote work and digital hiring platforms. Automated fraudulent job detection helps candidates audit listings quickly before disclosing personal details or paying application fees.

### How It Works:
- **Natural Language Processing**: Preprocesses textual data to remove formatting noise, punctuation, and casing discrepancies.
- **Machine Learning**: Extracts semantic relationships using a Term Frequency-Inverse Document Frequency (TF-IDF) representation and classifies the listing using a trained Linear Support Vector Machine (SVM) model.
- **OCR Engine Integration**: Enables users to submit job posting screenshots directly. The system cleans the image, extracts text, and passes it to the classification pipeline.
- **Interactive Interface**: Users can log in to run text analyses, upload images, and review their history, while administrators monitor traffic trends and view machine learning metrics.

---

## ✨ Key Features

- **User Registration**: Create accounts with built-in format validation (email regex) and disposable domain blocks (e.g. `mailinator.com`, `tempmail.com` are blocked).
- **User Login**: Access user dashboards with custom password strength validation.
- **JWT & Session Authentication**: Session-based auth for server-side HTML rendering, and stateless JWT (`Authorization: Bearer <token>`) authentication for REST endpoints.
- **Role-Based Access Control**: Differentiates views and controls between standard users (`USER`) and administrators (`ADMIN`).
- **Job Description Analysis**: Standard text field for pasting job postings, providing classification feedback.
- **Image-Based Job Analysis**: Screenshot upload zone using OpenCV and Tesseract OCR to extract text and analyze the listing.
- **User Dashboard**: Shows total scans performed, safety/risk distribution ratios, and history of past analyses.
- **Admin Dashboard**: Offers centralized statistics (total users, admins, predictions, and fake detection rates), prediction logs, a list of registered users, and interactive graphs showing daily traffic.
- **Model Evaluation Panel**: Integrates trained model performance metrics (Accuracy, F1-Score) directly into the admin panel.
- **Administrative Controls**: Allows promoting users to admin roles or demoting them back to users.
- **Secure Logout**: Clears session states and tokens cleanly.
- **Error Handling**: Graceful feedback on invalid input, missing database records, or image processing errors.

---

## 🛠️ Technology Stack

| Component | Technologies Used |
| :--- | :--- |
| **Frontend** | React, Vite, JavaScript, CSS (Decoupled Portal); Jinja2 templates, Glassmorphism CSS, Vanilla JS (Flask UI) |
| **Backend** | Python, Flask, Flask-CORS, Flask-WTF, Flask-JWT-Extended, Authlib, Gunicorn |
| **Machine Learning / NLP** | Scikit-learn, TF-IDF Vectorizer, Linear Support Vector Machine (SVM), Logistic Regression, Naive Bayes |
| **OCR / Image Processing** | OpenCV, Pytesseract (Tesseract OCR) |
| **Authentication** | JSON Web Tokens (JWT), Flask Session Cookies |
| **Database** | SQLite3 (`users.db`) |

---

## 🤖 Machine Learning Pipeline

```
Job Description
      ↓
Text Preprocessing  (Lowercase, remove special characters/punctuation, normalize whitespace)
      ↓
TF-IDF Extraction   (TfidfVectorizer: unigrams & bigrams, max 5000 features, English stop words)
      ↓
Linear SVM Model    (LinearSVC classifier trained on job description datasets)
      ↓
   Prediction       (Inference returning hard/soft classification threshold)
      ↓
Real / Fake Result  (Outputs classification category with a corresponding safety/risk score)
```

- **Inference Stage**: The pipeline relies on the saved TF-IDF vectorizer (`Model/tfidf.pkl`) and the best performing model (`Model/best_model.pkl` — trained as a Linear SVM).
- **Fallback Calibration**: The classifier uses a keyword-triggered threshold calibration. If common risk phrases are identified (e.g. "no experience", "weekly pay"), the classification sensitivity increases.

---

## 🖼️ Image / OCR Pipeline

```
Job Posting Image
      ↓
  Image Upload      (Flask Multi-part Form upload)
      ↓
OCR / Text Extraction (OpenCV Grayscale conversion + Tesseract OCR extraction)
      ↓
Text Preprocessing  (Normalization using re regex patterns)
      ↓
     TF-IDF         (Transforms extracted text into TF-IDF vector)
      ↓
Linear SVM Model    (Inference running on best_model.pkl)
      ↓
 Prediction Result  (JSON response showing extracted text, category, and probability)
```

This pipeline allows users to upload screenshots of advertisements directly, eliminating the need to type out descriptions manually.

---

## 🛡️ Security & Authentication

- **State & Token Isolation**: Secure session variables manage browser authentication. JWT tokens authenticate requests to RESTful routes.
- **Protected Routes**: Decorators (like `@jwt_required()` in python) protect endpoints from unauthenticated access.
- **Input Sanitization**: Uses regular expression checks to validate registration emails and blocks temporary/spam address domains.
- **File Upload Restrictions**: Enforces filename security (`secure_filename`) and blocks non-image formats (only `png`, `jpg`, `jpeg`, `webp` extensions are allowed).
- **Secure Password Storage**: Passwords are saved as pbkdf2-sha256 hashes (`generate_password_hash` and `check_password_hash`).

---

## 👥 User and Admin Functionality

### User Features
- **Register & Login**: Access pages with automated validation checking.
- **Job Description Predictor**: Paste descriptions and receive safety audit results.
- **Image Scan OCR**: Upload screenshots and view extracted text alongside safety reports.
- **Dashboard**: Track scans and view historical prediction trends.
- **Profile**: View account metadata.
- **Logout**: Revoke active session tokens.

### Admin Features
- **Admin Dashboard**: Real-time counters showing system users, administrative accounts, predictions, and detected fake rates.
- **User Directory**: View list of registered accounts with last login timestamps.
- **Prediction logs**: Audit logs showing user submissions and prediction outcomes.
- **Activity Graph**: SQLite-grouped metrics visualizing user engagement over 30 days.
- **Administrative promotion**: Promote users to `ADMIN` or demote administrators back to standard `USER` status.

---

## 📂 Project Structure

```
JobCheck/
├── backend/
│   ├── App/                  # Core application package
│   │   ├── app.py            # Main application factory
│   │   ├── config.py         # Paths and configurations
│   │   ├── database.py       # SQLite connection setup & migrations
│   │   ├── data_processor.py # Text preprocessing pipeline
│   │   └── routes.py         # Controller routes and REST API
│   ├── Dataset/              # Data directory
│   │   └── fake_job_postings.csv # Model dataset
│   ├── Model/                # Trained ML models and evaluation files
│   │   ├── best_model.pkl    # Trained Linear SVM Model
│   │   ├── tfidf.pkl         # Fitted TF-IDF Vectorizer
│   │   └── model_metadata.json # Best model metrics
│   ├── Static/               # Static assets (Glassmorphism styles, scripts)
│   ├── Templates/            # Jinja2 HTML templates
│   ├── tests/                # Automated unit tests
│   │   ├── test_jwt.py       # JWT auth tests
│   │   ├── test_ocr.py       # Dynamic Tesseract OCR tests
│   │   └── test_prediction.py # ML model prediction tests
│   ├── .env.example          # Environment variables template
│   ├── Dockerfile            # Container definition
│   ├── Procfile              # Deployment commands (Heroku/Render)
│   ├── render.yaml           # Render deployment configuration
│   ├── requirements.txt      # Python dependencies
│   └── wsgi.py               # WSGI production server entry point
├── frontend/                 # Decoupled React-Vite UI boilerplate
│   ├── public/               # Public assets
│   ├── src/                  # React source files
│   │   ├── components/       # UI Components folder
│   │   ├── pages/            # View pages folder
│   │   ├── services/         # API Connection services
│   │   │   └── api.js        # API service connection mapper
│   │   └── App.jsx           # React app shell
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite bundler options
├── .gitignore                # Global Git ignore rules
├── LICENSE                   # Software license (MIT)
└── README.md                 # Project root documentation
```

---

## ⚙️ Environment Variables

A `.env.example` file is included in the `backend/` directory to document environment variables. Create a local `.env` file inside the `backend/` directory to configure the application locally:

```env
# Flask configuration
SECRET_KEY=your-secure-secret-key-here

# JWT configuration
JWT_SECRET_KEY=your-jwt-secret-key-here

# Optional OAuth keys (OAuth logic uses standard authlib settings)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```
> [!IMPORTANT]
> Never commit your actual `.env` file containing secrets to GitHub.

---

## 🛠️ Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/NagaSaiRamesh06/detecting-fake-job-posts-using-nlp.git
cd detecting-fake-job-posts-using-nlp
```

### 2. Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows activation:
   .venv\Scripts\activate
   # Linux/Mac activation:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the SQLite database and seed the default admin account:
   ```bash
   python migrate.py
   ```

### 3. Frontend Setup
1. Open a separate terminal at the project root and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```

---

## ▶️ Running the Project Locally

### 1. Running the Flask Backend & Templates Server
From the `backend/` directory:
```bash
python -m App.app
```
The backend server runs on **`http://127.0.0.1:5000`** serving the monolithic Jinja2 user interface.
- *Default admin login: username `admin`, password `admin`.*

### 2. Running the Decoupled React/Vite UI
From the `frontend/` directory:
```bash
npm run dev
```
The React development server runs on **`http://localhost:5173`**.

---

## 📡 API Documentation

Important API routes exposed by the backend for decoupled client integration:

| Method | Endpoint | Purpose | Authentication |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/register` | Register new user account | No |
| **POST** | `/api/login` | Authenticate credentials & return JWT | No |
| **GET** | `/api/me` | Retrieve profile metadata | JWT |
| **POST** | `/predict` | Analyze job description text | JWT |
| **POST** | `/scan-image` | OCR extraction & job analysis | No (CSRF/Optional JWT) |
| **GET** | `/api/dashboard` | Fetch user prediction history stats | JWT |
| **GET** | `/api/admin` | Fetch system traffic and user listing | JWT |

---

## 🧪 Testing

The test suite is structured inside the **`backend/tests/`** directory.

To run the automated test suite:
```bash
cd backend
python -m unittest discover -s tests
```
The test suite validates:
- **Authentication**: Verifies JWT token retrieval and endpoint protection.
- **Model Predictions**: Verifies model prediction classifications.
- **OCR Engine**: Dynamically creates a text image, parses it via OpenCV/Tesseract, and verifies extracted keywords.

---

## 📊 Model Compatibility

- **Model format**: Precompiled models (`best_model.pkl`, `tfidf.pkl`) require **NumPy < 2.0.0** and compatible `scikit-learn` versions to run correctly.
- Installing NumPy 2.x will cause scikit-learn unpickling errors. Pinned versions are specified in the backend `requirements.txt`.

---

## ☁️ Deployment

Deployment configurations are included to run on hosting services such as Render or Heroku:
- **Dockerfile**: Implements a `python:3.9-slim` base image, installs system libraries (`tesseract-ocr`, `libgl1-mesa-glx`, `libglib2.0-0` for OpenCV), installs requirements, and runs via `gunicorn`.
- **Procfile**: Runs Gunicorn web workers (`web: gunicorn wsgi:app`).
- **render.yaml**: Automated deployment setup for Render.
- *Note: Deployment configuration is included for deployment to a compatible hosting platform.*

---

## ⚠️ Limitations

- **Dataset Dependability**: The classifier outputs depend on the statistical quality of the training dataset.
- **Prediction Thresholds**: Predictions indicate potential risk and do not serve as a legal validation of a job's status.
- **OCR Accuracy**: OCR extraction performance varies based on screenshot resolution, font clarity, and image compression quality.
- **Format Variations**: Model accuracy may vary on unseen job description formats.

---

## 🔮 Future Enhancements

- **Transformer Models**: Upgrade classifier pipeline to BERT or similar transformer models.
- **Advanced OCR Processing**: Integrate cloud-based OCR APIs for improved extraction.
- **Explainability**: Integrate SHAP or LIME visualizations to explain prediction attributes.
- **Broader Dataset Training**: Update models with recent verified listing feeds.

---

## 🖼️ Screenshots

### Login Page
`[Insert JobCheck Login Screenshot Here]`

### User Dashboard
`[Insert User Dashboard Screenshot Here]`

### Job Description Analysis
`[Insert Prediction Screenshot Here]`

### Image/OCR Analysis
`[Insert Scan Image Screenshot Here]`

### Admin Dashboard
`[Insert Admin Dashboard Screenshot Here]`
