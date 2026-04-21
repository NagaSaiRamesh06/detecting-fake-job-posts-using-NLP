from .database import get_db_connection
from werkzeug.security import generate_password_hash
import sqlite3

def fix_admin():
    print("Fixing admin user...")
    try:
        conn = get_db_connection()
        
        # 1. Ensure 'role' column exists (just in case)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
        except sqlite3.OperationalError:
            pass

        # 2. Upsert Admin User
        password = generate_password_hash('admin')
        
        # Check if admin exists
        cursor = conn.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone():
            print("Updating existing admin...")
            conn.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
        else:
            print("Creating new admin...")
            # We need to handle potential schema differences if table was created long ago
            # But with recent edits, it should have role.
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                        ('admin', password, 'ADMIN'))
        
        conn.commit()
        conn.close()
        print("Admin user fixed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_admin()
