import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.database import get_db_connection
from App.config import Config

def promote_admin(target_username=None):
    if not target_username:
        if len(sys.argv) > 1:
            target_username = sys.argv[1].strip()
        else:
            target_username = getattr(Config, 'ADMIN_USERNAME', 'admin')

    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if user exists
        c.execute("SELECT id, username, role FROM users WHERE username = %s", (target_username,))
        user = c.fetchone()
        
        if user:
            # Enforce single admin policy: Demote any other accounts with ADMIN role to USER
            c.execute("UPDATE users SET role = 'USER' WHERE role = 'ADMIN' AND username != %s", (target_username,))
            # Promote target user to ADMIN
            c.execute("UPDATE users SET role = 'ADMIN' WHERE username = %s", (target_username,))
            conn.commit()
            print(f"Success: '{target_username}' is now the sole ADMIN. All other accounts are USER.")
        else:
            print(f"Error: User '{target_username}' not found.")
            
        c.close()
        conn.close()
    except Exception as e:
        print(f"Error promoting admin: {e}")

if __name__ == "__main__":
    promote_admin()
