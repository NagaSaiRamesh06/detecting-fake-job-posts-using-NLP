import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.database import get_db_connection

def promote_admin():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if user exists
        c.execute("SELECT * FROM users WHERE username = %s", ('testuser@gmail.com',))
        user = c.fetchone()
        
        if user:
            c.execute("UPDATE users SET role = 'ADMIN' WHERE username = %s", ('testuser@gmail.com',))
            conn.commit()
            print("Success: 'testuser@gmail.com' promoted to ADMIN.")
        else:
            print("Error: User 'testuser@gmail.com' not found.")
            
        c.close()
        conn.close()
    except Exception as e:
        print(f"Error promoting admin: {e}")

if __name__ == "__main__":
    promote_admin()
