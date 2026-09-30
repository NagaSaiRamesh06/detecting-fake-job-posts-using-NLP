import os
import sys

# Ensure backend directory is in sys.path when run directly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.database import get_db_connection
from App.config import Config
from werkzeug.security import generate_password_hash

def fix_admin():
    print("Fixing admin user...")
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # 1. Ensure 'role' column exists (just in case)
        try:
            c.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'USER'")
            conn.commit()
        except Exception:
            conn.rollback()  # Rollback transaction on failure (e.g. column already exists)

        # 2. Ensure Primary Admin User exists with role ADMIN
        admin_user = getattr(Config, 'ADMIN_USERNAME', 'admin')
        admin_pwd = getattr(Config, 'ADMIN_DEFAULT_PASSWORD', 'admin')

        c.execute("SELECT id, username, role FROM users WHERE username = %s", (admin_user,))
        existing_admin = c.fetchone()
        if existing_admin:
            print(f"Ensuring role 'ADMIN' for primary admin: {admin_user}...")
            c.execute("UPDATE users SET role = 'ADMIN' WHERE username = %s", (admin_user,))
        else:
            print(f"Creating new primary admin: {admin_user}...")
            c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                      (admin_user, generate_password_hash(admin_pwd), 'ADMIN'))

        # 3. Demote all other admin accounts to 'USER' to enforce single admin policy
        c.execute("UPDATE users SET role = 'USER' WHERE role = 'ADMIN' AND username != %s", (admin_user,))
        
        conn.commit()
        c.close()
        conn.close()
        print("Admin user fixed successfully: exactly one admin account exists.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_admin()
