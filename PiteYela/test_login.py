"""Quick test script to verify login credentials."""
import sys
sys.path.insert(0, 'app')

from app.auth import login

print("Testing login credentials...")
print("=" * 50)

# Test admin login
success, user, msg = login('admin', 'admin123')

if success:
    print("[SUCCESS] LOGIN SUCCESSFUL!")
    print(f"Username: {user['username']}")
    print(f"Full Name: {user['full_name']}")
    print(f"Role: {user['role']}")
    print()
    print("You can use these credentials to login:")
    print("  Username: admin")
    print("  Password: admin123")
else:
    print("[FAILED] LOGIN FAILED!")
    print(f"Error: {msg}")
    print()
    print("The admin user may not exist. Run:")
    print("  python init_database.py")

print("=" * 50)

