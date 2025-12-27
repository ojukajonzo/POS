"""
Database connection and schema management for Alcohol POS System.
Handles SQLite database initialization, table creation, and transaction management.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Tuple, Any
from app.config import DB_PATH, DATA_DIR

def get_connection() -> sqlite3.Connection:
    """Get a database connection with proper settings."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def execute_transaction(queries: List[Tuple[str, Tuple]]) -> bool:
    """
    Execute multiple queries in a single transaction.
    
    Args:
        queries: List of (sql_query, params) tuples
        
    Returns:
        True if all queries succeed, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for query, params in queries:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Transaction error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def init_db() -> None:
    """Initialize database schema and create default admin user if needed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                milliliters INTEGER DEFAULT 0,
                cost_price REAL NOT NULL DEFAULT 0,
                selling_price REAL NOT NULL DEFAULT 0,
                profit REAL NOT NULL DEFAULT 0,
                quantity_stocked INTEGER NOT NULL DEFAULT 0,
                quantity_sold INTEGER NOT NULL DEFAULT 0,
                quantity_available INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add milliliters column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN milliliters INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cashier_id INTEGER NOT NULL,
                cashier_name TEXT NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                grand_total REAL NOT NULL,
                FOREIGN KEY (cashier_id) REFERENCES users(id)
            )
        """)
        
        # Sale items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                milliliters INTEGER DEFAULT 0,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)")
        
        conn.commit()
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Create default admin user (username: admin, password: admin123)
            import bcrypt
            default_password = "admin123"
            password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            """, ("admin", password_hash.decode('utf-8'), "admin", "Administrator"))
            conn.commit()
            print("Default admin user created: username='admin', password='admin123'")
        
    except Exception as e:
        conn.rollback()
        print(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

    # Ensure old databases have the milliliters column on sale_items
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE sale_items ADD COLUMN milliliters INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists or table missing; ignore
            pass
    finally:
        conn.close()

def test_connection() -> bool:
    """Test database connection."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

