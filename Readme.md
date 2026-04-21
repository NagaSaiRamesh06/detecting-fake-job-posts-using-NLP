# JobCheck - Fake Job Prediction System

Welcome to the **JobCheck** project! JobCheck is an advanced, AI-powered web application designed to combat recruitment fraud by detecting fake job postings in real-time.

This project is structured into two main components:

- **[Backend](./backend/)**: A Flask-based API that handles Machine Learning predictions (Linear SVM, TF-IDF), Image OCR (Tesseract), User Authentication, and Database management.
- **[Frontend](./frontend/)**: A modern, interactive user interface built with React and Vite.

## 🚀 Getting Started

### 1. Start the Backend Server

Navigate to the `backend` directory and follow the setup instructions in the [Backend README](./backend/Readme.md).

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```
*(Runs on `http://127.0.0.1:5000`)*

### 2. Start the Frontend Development Server

Navigate to the `frontend` directory and follow the instructions in the [Frontend README](./frontend/README.md).

```bash
cd frontend
npm install
npm run dev
```
*(Runs on `http://localhost:5173`)*

## 📂 Project Structure

```
JobCheck/
├── backend/       # Flask backend API, Models, and Database
└── frontend/      # React + Vite frontend application
```

## 🤝 Overview

This system utilizes advanced NLP and ML to provide a highly accurate detection system. The frontend offers an elegant Glassmorphism UI, a dashboard for users, and a comprehensive admin panel for traffic and analytics monitoring.
