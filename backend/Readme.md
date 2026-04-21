# JobCheck - Fake Job Prediction System

![JobCheck Design](https://via.placeholder.com/800x300?text=JobCheck+AI+Dashboard)

**JobCheck** is an advanced, AI-powered web application designed to combat recruitment fraud. Leveraging Natural Language Processing (NLP) and Machine Learning, it detects fake job postings in real-time with **96% accuracy**. The system features a modern, professional "Glassmorphism" UI, OCR capabilities for image analysis, and a comprehensive admin dashboard.

## ✨ Key Features

-   **🤖 Advanced AI Model**:
    -   Utilizes **TF-IDF Vectorization** for text feature extraction.
    -   Powered by a **Linear SVM** (ranked as the best model via AutoML optimization).
    -   Trained on a dataset of 18,000+ job descriptions.
-   **📷 Image Scanning (OCR)**:
    -   Integrated with **Tesseract OCR** and **OpenCV**.
    -   Allows users to upload screenshots of job ads for instant analysis.
-   **📊 Interactive Dashboard**:
    -   Real-time classification confidence scores (Risk vs. Safety).
    -   User-friendly interface with responsive sidebar navigation.
-   **🛡️ Secure Authentication**:
    -   Robust Registration & Login (Session-based).
    -   Password Strength Meter and Confirmation validation.
    -   Admin Role management and secure backend routes.
-   **📈 Admin Analytics**:
    -   Monitor system traffic, prediction logs, and model performance metrics (Accuracy, F1-Score).

## 🛠️ Tech Stack

-   **Backend**: Python, Flask, SQLite
-   **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Vanilla)
-   **Machine Learning**: Scikit-learn, Pandas, NumPy
-   **OCR**: Pytesseract, OpenCV
-   **Tools**: Git, Virtualenv

## 🚀 Installation & Setup

### 1. Prerequisites
-   Python 3.9+ installed.
-   [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed (Path: `C:\Program Files\Tesseract-OCR\tesseract.exe`).

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/JobCheck.git
cd JobCheck
```

### 3. Create Virtual Environment
```bash
python -m venv .venv
# Activate:
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Mac/Linux
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```
*Key dependencies: `flask`, `scikit-learn`, `pandas`, `opencv-python`, `pytesseract`*

### 5. Database Migration
Initialize the database and apply the latest schema:
```bash
python migrate.py
```

## ▶️ Running the Application

Start the Flask development server:
```bash
python -m App.app
```

Access the application at: **`http://127.0.0.1:5000`**

### Test Credentials
-   **Admin User**: `admin` / `admin` (or registered email)

## 📂 Project Structure

```
JobCheck/
├── App/
│   ├── app.py              # Main Application Entry Point
│   ├── routes.py           # Flask Routes & API Logic
│   ├── database.py         # DB Connection & Schema
│   ├── data_processor.py   # NLP Preprocessing Pipeline
│   ├── feature_engineering.py # TF-IDF Logic
│   └── automl_sklearn.py   # Model Comparison Script
├── Model/
│   ├── best_model.pkl      # Trained Linear SVM Model
│   ├── tfidf.pkl           # TF-IDF Vectorizer
│   └── model_metadata.json # Performance Metrics
├── Static/
│   ├── styles.css          # Global Styles
│   └── auth.js             # Client-side validation
├── Templates/              # HTML Templates (Jinja2)
├── users.db                # SQLite Database
└── migrate.py              # Database Migration Tool
```

## 🤝 Contribution
Developed for Academic Submission.
