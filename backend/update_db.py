import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'App/users.db')

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if column exists first to avoid error
        c.execute("PRAGMA table_info(predictions)")
        columns = [info[1] for info in c.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding 'created_at' column to predictions table...")
            c.execute("ALTER TABLE predictions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("Successfully added 'created_at' column.")
        else:
            print("'created_at' column already exists.")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
        
    conn.close()

if __name__ == "__main__":
    update_schema()
