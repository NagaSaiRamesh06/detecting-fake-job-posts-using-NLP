import psycopg2
from .database import get_db_connection
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
        except psycopg2.Error:
            conn.rollback()  # Rollback transaction on failure (e.g. column already exists)

        # 2. Upsert Admin User
        password = generate_password_hash('admin')
        
        # Check if admin exists
        c.execute("SELECT * FROM users WHERE username = 'admin'")
        if c.fetchone():
            print("Updating existing admin...")
            c.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
        else:
            print("Creating new admin...")
            c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                      ('admin', password, 'ADMIN'))
        
        conn.commit()
        c.close()
        conn.close()
        print("Admin user fixed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_admin()
