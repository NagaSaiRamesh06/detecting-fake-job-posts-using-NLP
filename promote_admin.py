import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'App/users.db')

def promote_admin():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE username = 'testuser@gmail.com'")
    user = c.fetchone()
    
    if user:
        c.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'testuser@gmail.com'")
        conn.commit()
        print("Success: 'testuser@gmail.com' promoted to ADMIN.")
    else:
        print("Error: User 'testuser@gmail.com' not found.")
        
    conn.close()

if __name__ == "__main__":
    promote_admin()
