import sqlite3
from werkzeug.security import generate_password_hash
from .config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Enable Foreign Keys
    c.execute("PRAGMA foreign_keys = ON")

    # 1. Users Table (Updated Schema)
    # We use a try-catch pattern to add columns if they don't exist (Simple Migration)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
    except sqlite3.OperationalError:
        pass # Column likely exists

    try:
        c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE users ADD COLUMN name TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE users ADD COLUMN fullname TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    # 2. Predictions Table (New)
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  input_text TEXT, 
                  prediction_result TEXT, 
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Check if admin exists, if not create one
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        print("Creating default admin user...")
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ('admin', generate_password_hash('admin'), 'ADMIN'))
    else:
        # Ensure existing admin has ADMIN role
        c.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
    
    conn.commit()
    conn.close()
