"""
Authentication and authorization for Alcohol POS System.
Handles login, password hashing, and role checking.
"""
import bcrypt
import sqlite3
from typing import Optional, Dict
from app.database import get_connection

# Global session storage
_current_user: Optional[Dict] = None

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def login(username: str, password: str) -> tuple[bool, Optional[Dict], str]:
    """
    Attempt to login user.
    
    Returns:
        (success, user_dict, error_message)
    """
    global _current_user
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, password_hash, role, full_name, is_active
            FROM users
            WHERE username = ? AND is_active = 1
        """, (username,))
        
        row = cursor.fetchone()
        if not row:
            return False, None, "Invalid username or password"
        
        if not verify_password(password, row['password_hash']):
            return False, None, "Invalid username or password"
        
        user = {
            'id': row['id'],
            'username': row['username'],
            'role': row['role'],
            'full_name': row['full_name']
        }
        
        _current_user = user
        return True, user, ""
        
    except Exception as e:
        return False, None, f"Login error: {str(e)}"
    finally:
        conn.close()

def logout():
    """Logout current user."""
    global _current_user
    _current_user = None

def get_current_user() -> Optional[Dict]:
    """Get current logged-in user."""
    return _current_user

def is_admin() -> bool:
    """Check if current user is admin."""
    return _current_user is not None and _current_user.get('role') == 'admin'

def is_cashier() -> bool:
    """Check if current user is cashier."""
    return _current_user is not None and _current_user.get('role') == 'cashier'

def require_admin(func):
    """Decorator to require admin role."""
    def wrapper(*args, **kwargs):
        if not is_admin():
            raise PermissionError("Admin access required")
        return func(*args, **kwargs)
    return wrapper

def create_user(username: str, password: str, role: str, full_name: str) -> tuple[bool, str]:
    """
    Create a new user (admin only).
    
    Returns:
        (success, error_message)
    """
    if role not in ['admin', 'cashier']:
        return False, "Invalid role"
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, full_name))
        
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"
    finally:
        conn.close()

def get_all_users() -> list[Dict]:
    """Get all users (admin only)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, role, full_name, created_at, is_active
            FROM users
            ORDER BY created_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

