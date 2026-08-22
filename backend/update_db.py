import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from App.database import get_db_connection

def update_schema():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if column exists in PostgreSQL
        c.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'predictions' AND column_name = 'created_at'
        """)
        column_exists = c.fetchone() is not None
        
        if not column_exists:
            print("Adding 'created_at' column to predictions table...")
            c.execute("ALTER TABLE predictions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("Successfully added 'created_at' column.")
        else:
            print("'created_at' column already exists.")
            
        c.close()
        conn.close()
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
