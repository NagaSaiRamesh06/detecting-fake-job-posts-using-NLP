import os

class Config:
    # Use environment variable for secret key, or default to a secure random string (for dev)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-super-secret-key-change-in-prod'
    
    # Path setup
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploads')
    DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
    
    # Model Paths
    MODEL_DIR = os.path.join(BASE_DIR, "Model")
    TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf.pkl")
    MODEL_PATH = os.path.join(MODEL_DIR, "best_model.pkl")

    # App Config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # OAuth Config
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string-change-this'
