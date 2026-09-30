import os
import re
import sqlite3
from werkzeug.security import generate_password_hash
from .config import Config

try:
    import psycopg2
    import psycopg2.extensions
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

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

if PSYCOPG2_AVAILABLE:
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
else:
    DictAndTupleCursor = None

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def _adapt_sql(self, sql):
        # Convert %s placeholder to ? for sqlite parameter binding
        return re.sub(r'(?<!%)\%s', '?', sql)

    def execute(self, sql, parameters=None):
        adapted = self._adapt_sql(sql)
        if parameters is None:
            return self._cursor.execute(adapted)
        return self._cursor.execute(adapted, parameters)

    def executemany(self, sql, seq_of_parameters):
        adapted = self._adapt_sql(sql)
        return self._cursor.executemany(adapted, seq_of_parameters)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def close(self):
        self._cursor.close()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def execute(self, sql, parameters=None):
        return self.cursor().execute(sql, parameters)

def is_postgres():
    db_url = Config.DATABASE_URL
    return bool(db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")))

def get_db_connection():
    db_url = Config.DATABASE_URL
    if is_postgres():
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL connections.")
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(db_url, cursor_factory=DictAndTupleCursor)
        return conn
    
    # Fallback to local SQLite database
    db_path = getattr(Config, 'DB_PATH', os.path.join(os.path.dirname(__file__), 'users.db'))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Custom function for PostgreSQL compatibility: TO_CHAR(created_at, 'YYYY-MM-DD')
    conn.create_function("TO_CHAR", 2, lambda dt, fmt: str(dt)[:10] if dt else '')
    return SQLiteConnectionWrapper(conn)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    if is_postgres():
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
    else:
        # SQLite Schema
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username VARCHAR(255) UNIQUE, 
                      password VARCHAR(255),
                      role VARCHAR(50) DEFAULT 'USER',
                      last_login VARCHAR(50),
                      name VARCHAR(255),
                      fullname VARCHAR(255),
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS predictions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user_id INTEGER REFERENCES users(id), 
                      input_text TEXT, 
                      prediction_result VARCHAR(255), 
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Ensure primary admin exists with role ADMIN
    admin_user = getattr(Config, 'ADMIN_USERNAME', 'admin')
    c.execute("SELECT * FROM users WHERE username = %s", (admin_user,))
    if not c.fetchone():
        print(f"Creating default admin user: {admin_user}...")
        admin_pwd = getattr(Config, 'ADMIN_DEFAULT_PASSWORD', 'admin')
        c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                  (admin_user, generate_password_hash(admin_pwd), 'ADMIN'))
    else:
        # Ensure existing primary admin has ADMIN role without altering credentials
        c.execute("UPDATE users SET role = 'ADMIN' WHERE username = %s", (admin_user,))
    
    # Enforce strictly SINGLE admin policy: demote any other admin accounts to USER
    c.execute("UPDATE users SET role = 'USER' WHERE role = 'ADMIN' AND username != %s", (admin_user,))
    
    conn.commit()
    c.close()
    conn.close()
