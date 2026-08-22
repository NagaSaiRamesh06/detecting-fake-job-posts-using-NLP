import psycopg2
import psycopg2.extensions
from werkzeug.security import generate_password_hash
from .config import Config

class DictAndTupleRow(dict):
    def __init__(self, cursor, row):
        super().__init__()
        self._keys = [desc[0] for desc in cursor.description] if cursor.description else []
        self._values = row
        for key, val in zip(self._keys, row):
            self[key] = val

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)

class DictAndTupleCursor(psycopg2.extensions.cursor):
    def fetchone(self):
        row = super().fetchone()
        if row is None:
            return None
        return DictAndTupleRow(self, row)

    def fetchall(self):
        rows = super().fetchall()
        return [DictAndTupleRow(self, row) for row in rows]

    def fetchmany(self, size=None):
        rows = super().fetchmany(size)
        return [DictAndTupleRow(self, row) for row in rows]

def get_db_connection():
    db_url = Config.DATABASE_URL
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    # Render database URLs sometimes start with postgres://, which is compatible but let's normalize it to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    conn = psycopg2.connect(db_url, cursor_factory=DictAndTupleCursor)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Users Table (PostgreSQL Schema)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id SERIAL PRIMARY KEY, 
                  username VARCHAR(255) UNIQUE, 
                  password VARCHAR(255),
                  role VARCHAR(50) DEFAULT 'USER',
                  last_login VARCHAR(50),
                  name VARCHAR(255),
                  fullname VARCHAR(255),
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. Predictions Table (PostgreSQL Schema)
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id SERIAL PRIMARY KEY, 
                  user_id INTEGER REFERENCES users(id), 
                  input_text TEXT, 
                  prediction_result VARCHAR(255), 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Check if admin exists, if not create one
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        print("Creating default admin user...")
        c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                  ('admin', generate_password_hash('admin'), 'ADMIN'))
    else:
        # Ensure existing admin has ADMIN role
        c.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
    
    conn.commit()
    c.close()
    conn.close()
