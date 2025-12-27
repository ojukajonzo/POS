"""
Password change module for Alcohol POS System.
Allows users to change their own password.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QLabel, QMessageBox)
from app.database import get_connection
from app.auth import get_current_user, verify_password, hash_password
from app.utils import show_error_dialog, show_info_dialog

class PasswordChangeDialog(QDialog):
    """Dialog for changing password."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PiteYelaHouseofWine_POS - Change Password")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setPlaceholderText("Enter current password")
        form.addRow("Current Password:", self.current_password_input)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new password")
        form.addRow("New Password:", self.new_password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        form.addRow("Confirm Password:", self.confirm_password_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.change_btn = QPushButton("Change Password")
        self.change_btn.clicked.connect(self.change_password)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
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
        self.change_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        button_layout.addWidget(self.change_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set focus
        self.current_password_input.setFocus()
    
    def change_password(self):
        """Change the password."""
        current_user = get_current_user()
        if not current_user:
            show_error_dialog(self, "Error", "User session expired. Please login again.")
            self.reject()
            return
        
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate
        if not current_password:
            show_error_dialog(self, "Validation Error", "Please enter your current password")
            return
        
        if not new_password:
            show_error_dialog(self, "Validation Error", "Please enter a new password")
            return
        
        if len(new_password) < 4:
            show_error_dialog(self, "Validation Error", "New password must be at least 4 characters long")
            return
        
        if new_password != confirm_password:
            show_error_dialog(self, "Validation Error", "New passwords do not match")
            return
        
        # Verify current password
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (current_user['id'],))
            row = cursor.fetchone()
            
            if not row or not verify_password(current_password, row['password_hash']):
                show_error_dialog(self, "Error", "Current password is incorrect")
                self.current_password_input.clear()
                self.current_password_input.setFocus()
                return
            
            # Update password
            new_password_hash = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                         (new_password_hash, current_user['id']))
            conn.commit()
            
            show_info_dialog(self, "Success", "Password changed successfully!")
            self.accept()
            
        except Exception as e:
            show_error_dialog(self, "Error", f"Failed to change password: {str(e)}")
        finally:
            conn.close()

