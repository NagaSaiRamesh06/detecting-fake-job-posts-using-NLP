import os

# Load .env file if present without requiring external packages
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(_env_path):
    try:
        with open(_env_path, 'r', encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith('#') and '=' in _line:
                    _k, _v = _line.split('=', 1)
                    _k = _k.strip()
                    _v = _v.strip().strip('"').strip("'")
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        pass

class Config:
    # Use environment variable for secret key, or default to a secure random string (for dev)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-super-secret-key-change-in-prod'
    
    # Path setup
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploads')
    
    # Database config
    DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Admin Account Config (Single Admin Policy)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin')
    
    # Model Paths
    MODEL_DIR = os.path.join(BASE_DIR, "Model")
    TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf.pkl")
    MODEL_PATH = os.path.join(MODEL_DIR, "best_model.pkl")

    # App Config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string-change-this'

    # Security & Cookie Settings
    IS_PRODUCTION = bool(os.environ.get('RENDER')) or bool(os.environ.get('RENDER_EXTERNAL_URL')) or os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    PREFERRED_URL_SCHEME = 'https' if IS_PRODUCTION else 'http'
