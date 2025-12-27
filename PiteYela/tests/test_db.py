"""
Basic database tests for Alcohol POS System.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_connection, test_connection
from app.models import get_product, create_sale
from app.auth import login, create_user

def test_database_init():
    """Test database initialization."""
    print("Testing database initialization...")
    try:
        init_db()
        assert test_connection(), "Database connection failed"
        print("[OK] Database initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

def test_user_creation():
    """Test user creation and login."""
    print("Testing user creation and login...")
    try:
        # Test login with default admin
        success, user, msg = login("admin", "admin123")
        assert success, f"Default admin login failed: {msg}"
        print("[OK] Default admin login successful")
        return True
    except Exception as e:
        print(f"[ERROR] User test failed: {e}")
        return False

def test_product_operations():
    """Test product operations."""
    print("Testing product operations...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert test product
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, description, cost_price, selling_price, profit, quantity_stocked, quantity_available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("TEST001", "Test Product", "Test Description", 10.0, 15.0, 5.0, 100, 100))
        conn.commit()
        
        # Retrieve product
        product = get_product("TEST001")
        assert product is not None, "Product not found"
        assert product.name == "Test Product", "Product name mismatch"
        assert product.profit == 5.0, "Profit calculation error"
        assert product.quantity_available == 100, "Quantity available error"
        
        print("[OK] Product operations successful")
        return True
    except Exception as e:
        print(f"[ERROR] Product test failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running database tests...\n")
    
    results = []
    results.append(test_database_init())
    results.append(test_user_creation())
    results.append(test_product_operations())
    
    print(f"\nTests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)

