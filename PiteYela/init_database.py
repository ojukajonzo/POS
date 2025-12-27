"""
Standalone script to initialize the database.
Run this once to set up the database schema and create default admin user.
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import DATA_DIR, DB_PATH
from app.database import init_db, test_connection

def main():
    """Initialize database."""
    print("Alcohol POS - Database Initialization")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Database path: {DB_PATH}")
    print()
    
    # Ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Data directory created/verified: {DATA_DIR}")
    
    # Initialize database
    try:
        print("Initializing database schema...")
        init_db()
        print("[OK] Database schema created successfully")
        
        # Test connection
        if test_connection():
            print("[OK] Database connection test passed")
        else:
            print("[ERROR] Database connection test failed")
            return 1
        
        print()
        print("=" * 50)
        print("Database initialization complete!")
        print()
        print("Default admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        print("IMPORTANT: Change the default password after first login!")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

