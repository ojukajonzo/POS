"""
Main entry point for Alcohol POS System.
Handles application initialization, database setup, and window routing.
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import BASE_DIR, DATA_DIR, DB_PATH
from app.database import init_db, test_connection
from app.auth import login, logout
from app.pos import POSWindow

class LoginWindow:
    """Simple login window using QMessageBox for input."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.user = None
    
    def show_login(self):
        """Show login dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout
        
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Login - PiteYelaHouseofWine_POS")
        dialog.setModal(True)
        dialog.resize(350, 200)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Password:", self.password_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(lambda: self.attempt_login(dialog))
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(dialog.reject)
        
        button_style = """
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                padding: 8px 16px;
                border-radius: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """
        self.login_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Set focus and Enter key
        self.username_input.setFocus()
        self.password_input.returnPressed.connect(lambda: self.attempt_login(dialog))
        self.login_btn.setDefault(True)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return self.user
        return None
    
    def attempt_login(self, dialog):
        """Attempt to login with entered credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(dialog, "Login Error", "Please enter both username and password.")
            return
        
        success, user, error_msg = login(username, password)
        
        if success:
            self.user = user
            dialog.accept()
        else:
            QMessageBox.critical(dialog, "Login Failed", error_msg)
            self.password_input.clear()
            self.password_input.setFocus()

def check_admin_privileges():
    """Check if running with admin privileges (optional check)."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return True  # Assume admin if check fails

def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("PiteYelaHouseofWine_POS")
    app.setQuitOnLastWindowClosed(True)
    
    # Load stylesheet
    try:
        from pathlib import Path
        # Handle both development and PyInstaller bundle paths
        if getattr(sys, 'frozen', False):
            # Running as bundled executable
            bundle_dir = Path(sys._MEIPASS)
            stylesheet_path = bundle_dir / "assets" / "styles.qss"
        else:
            # Running from source
            stylesheet_path = Path(__file__).parent.parent / "assets" / "styles.qss"
        if stylesheet_path.exists():
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    try:
        print("Initializing database...")
        init_db()
        print("Database initialized successfully.")
        
        if not test_connection():
            QMessageBox.critical(None, "Database Error", 
                               "Failed to connect to database. Please check file permissions.")
            return 1
    except Exception as e:
        QMessageBox.critical(None, "Database Error", 
                           f"Failed to initialize database:\n{str(e)}")
        return 1
    
    # Show login
    login_window = LoginWindow()
    user = login_window.show_login()
    
    if not user:
        # User cancelled login
        return 0
    
    # Show POS window
    try:
        pos_window = POSWindow()
        pos_window.show()
        
        # Run application
        return app.exec()
    except Exception as e:
        QMessageBox.critical(None, "Application Error", 
                           f"Failed to start application:\n{str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        logout()

if __name__ == "__main__":
    sys.exit(main())

