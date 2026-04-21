from App.database import init_db

if __name__ == "__main__":
    print("Running database migration...")
    init_db()
    print("Database migration completed.")
