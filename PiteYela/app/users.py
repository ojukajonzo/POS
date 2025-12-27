"""
User management module for Alcohol POS System.
Admin-only user creation, editing, and management.
"""
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QDialog, QFormLayout, QComboBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from app.database import get_connection
from app.auth import is_admin, create_user, get_all_users, hash_password, verify_password
from app.utils import show_error_dialog

class UserDialog(QDialog):
    """Dialog for adding/editing users."""
    
    def __init__(self, parent=None, user_id: Optional[int] = None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("PiteYelaHouseofWine_POS - " + ("Add User" if not user_id else "Edit User"))
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout()
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setMaxLength(50)
        layout.addRow("Username:", self.username_input)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setMaxLength(100)
        layout.addRow("Full Name:", self.full_name_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["cashier", "admin"])
        layout.addRow("Role:", self.role_combo)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Leave empty to keep current password" if user_id else "Enter password")
        layout.addRow("Password:" if not user_id else "New Password (optional):", self.password_input)
        
        # Active status
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setChecked(True)
        layout.addRow("Active:", self.active_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
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
        self.save_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
        
        # Load existing user if editing
        if user_id:
            self.load_user()
        
        # Connect signals
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_user(self):
        """Load user data into form."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, full_name, role, is_active
                FROM users
                WHERE id = ?
            """, (self.user_id,))
            
            row = cursor.fetchone()
            if row:
                self.username_input.setText(row['username'])
                self.username_input.setReadOnly(True)  # Can't change username
                self.full_name_input.setText(row['full_name'])
                
                index = self.role_combo.findText(row['role'])
                if index >= 0:
                    self.role_combo.setCurrentIndex(index)
                
                self.active_checkbox.setChecked(bool(row['is_active']))
        finally:
            conn.close()
    
    def get_data(self) -> Dict:
        """Get form data."""
        return {
            'username': self.username_input.text().strip(),
            'full_name': self.full_name_input.text().strip(),
            'role': self.role_combo.currentText(),
            'password': self.password_input.text(),
            'is_active': self.active_checkbox.isChecked()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate form data."""
        data = self.get_data()
        
        if not data['username']:
            return False, "Username is required"
        
        if not data['full_name']:
            return False, "Full name is required"
        
        if not self.user_id and not data['password']:
            return False, "Password is required for new users"
        
        return True, ""

class UsersWindow(QWidget):
    """User management window (Admin only)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if not is_admin():
            show_error_dialog(self, "Access Denied", "Admin access required")
            return
        
        self.setWindowTitle("PiteYelaHouseofWine_POS - User Management")
        self.resize(800, 500)
        self.setStyleSheet("background-color: white;")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.close)
        self.add_btn = QPushButton("Add User")
        self.edit_btn = QPushButton("Edit User")
        self.delete_btn = QPushButton("Delete User")
        self.view_transactions_btn = QPushButton("View Transactions")
        self.view_transactions_btn.clicked.connect(self.view_transactions)
        self.refresh_btn = QPushButton("Refresh")
        
        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.view_transactions_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Role", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ccc;
                gridline-color: #e0e0e0;
                background-color: white;
                selection-background-color: #4CAF50;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_user)
        self.edit_btn.clicked.connect(self.edit_user)
        self.delete_btn.clicked.connect(self.delete_user)
        self.refresh_btn.clicked.connect(self.refresh_table)
        
        # Load data
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh user table."""
        users = get_all_users()
        self.table.setRowCount(len(users))
        
        for row_idx, user in enumerate(users):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(user['username']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user['full_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(user['role'].title()))
            status = "Active" if user['is_active'] else "Inactive"
            self.table.setItem(row_idx, 4, QTableWidgetItem(status))
        
        self.table.resizeColumnsToContents()
    
    def add_user(self):
        """Open dialog to add new user."""
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            valid, msg = dialog.validate()
            if not valid:
                show_error_dialog(self, "Validation Error", msg)
                return
            
            success, error_msg = create_user(
                username=data['username'],
                password=data['password'],
                role=data['role'],
                full_name=data['full_name']
            )
            
            if success:
                self.refresh_table()
                QMessageBox.information(self, "Success", "User added successfully")
            else:
                show_error_dialog(self, "Error", f"Failed to add user: {error_msg}")
    
    def edit_user(self):
        """Edit selected user."""
        selected = self.table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select a user to edit")
            return
        
        user_id = int(self.table.item(selected[0].row(), 0).text())
        dialog = UserDialog(self, user_id)
        
        if dialog.exec():
            data = dialog.get_data()
            valid, msg = dialog.validate()
            if not valid:
                show_error_dialog(self, "Validation Error", msg)
                return
            
            conn = get_connection()
            try:
                cursor = conn.cursor()
                
                # Update user
                if data['password']:
                    # Update password
                    password_hash = hash_password(data['password'])
                    cursor.execute("""
                        UPDATE users
                        SET full_name = ?, role = ?, is_active = ?, password_hash = ?
                        WHERE id = ?
                    """, (data['full_name'], data['role'], 1 if data['is_active'] else 0,
                          password_hash, user_id))
                else:
                    # Don't update password
                    cursor.execute("""
                        UPDATE users
                        SET full_name = ?, role = ?, is_active = ?
                        WHERE id = ?
                    """, (data['full_name'], data['role'], 1 if data['is_active'] else 0, user_id))
                
                conn.commit()
                self.refresh_table()
                QMessageBox.information(self, "Success", "User updated successfully")
            except Exception as e:
                show_error_dialog(self, "Error", f"Failed to update user: {str(e)}")
            finally:
                conn.close()
    
    def delete_user(self):
        """Delete selected user (deactivate instead of delete)."""
        selected = self.table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select a user to delete")
            return
        
        user_id = int(self.table.item(selected[0].row(), 0).text())
        username = self.table.item(selected[0].row(), 1).text()
        
        # Prevent deleting yourself
        from app.auth import get_current_user
        current_user = get_current_user()
        if current_user and current_user['id'] == user_id:
            show_error_dialog(self, "Error", "You cannot delete your own account")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to deactivate user '{username}'?\n\nThis will prevent them from logging in.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
                conn.commit()
                self.refresh_table()
                QMessageBox.information(self, "Success", "User deactivated successfully")
            except Exception as e:
                show_error_dialog(self, "Error", f"Failed to deactivate user: {str(e)}")
            finally:
                conn.close()
    
    def view_transactions(self):
        """View transactions for selected cashier."""
        selected = self.table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select a user to view transactions")
            return
        
        user_id = int(self.table.item(selected[0].row(), 0).text())
        username = self.table.item(selected[0].row(), 1).text()
        full_name = self.table.item(selected[0].row(), 2).text()
        
        # Create transactions window
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
        from app.database import get_connection
        from app.utils import format_currency
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"PiteYelaHouseofWine_POS - Transactions for {full_name}")
        dialog.resize(900, 600)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"Sales Transactions for: {full_name} ({username})")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background-color: #f0f0f0; border: 2px solid #ccc;")
        layout.addWidget(header_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Sale ID", "Date", "Items", "Total Sales", "Total Cost", "Profit", "Details"
        ])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("border: 2px solid #ccc;")
        
        # Load transactions
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.sale_date, s.grand_total, COUNT(si.id) as item_count
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                WHERE s.cashier_id = ?
                GROUP BY s.id
                ORDER BY s.sale_date DESC
            """, (user_id,))
            
            sales = cursor.fetchall()
            table.setRowCount(len(sales))
            
            total_sales = 0.0
            total_cost = 0.0
            total_profit = 0.0
            
            for row_idx, sale in enumerate(sales):
                sale_id = sale['id']
                
                # Get sale items to calculate cost and profit
                cursor.execute("""
                    SELECT si.product_id, si.quantity, si.unit_price, si.line_total,
                           si.milliliters, p.cost_price
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                """, (sale_id,))
                
                items = cursor.fetchall()
                sale_cost = sum(item['cost_price'] * item['quantity'] for item in items)
                sale_profit = sale['grand_total'] - sale_cost
                
                total_sales += sale['grand_total']
                total_cost += sale_cost
                total_profit += sale_profit
                
                table.setItem(row_idx, 0, QTableWidgetItem(str(sale['id'])))
                table.setItem(row_idx, 1, QTableWidgetItem(sale['sale_date']))
                table.setItem(row_idx, 2, QTableWidgetItem(str(sale['item_count'])))
                table.setItem(row_idx, 3, QTableWidgetItem(format_currency(sale['grand_total'])))
                table.setItem(row_idx, 4, QTableWidgetItem(format_currency(sale_cost)))
                table.setItem(row_idx, 5, QTableWidgetItem(format_currency(sale_profit)))
                
                # Details button
                details_btn = QPushButton("View")
                details_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: black;
                        border: 2px solid #000000;
                        padding: 5px 10px;
                        border-radius: 0px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                        border: 2px solid #000000;
                    }
                """)
                details_btn.clicked.connect(lambda checked, sid=sale_id: self.show_sale_details(sid))
                table.setCellWidget(row_idx, 6, details_btn)
            
            table.resizeColumnsToContents()
            
            # Summary
            summary_label = QLabel(
                f"Total Sales: {format_currency(total_sales)} | "
                f"Total Cost: {format_currency(total_cost)} | "
                f"Total Profit: {format_currency(total_profit)} | "
                f"Transactions: {len(sales)}"
            )
            summary_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 10px; background-color: #e8f5e9; border: 2px solid #4CAF50;")
            layout.addWidget(summary_label)
            
        finally:
            conn.close()
        
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                padding: 8px 20px;
                border-radius: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_sale_details(self, sale_id: int):
        """Show detailed sale items."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
        from app.database import get_connection
        from app.utils import format_currency
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"PiteYelaHouseofWine_POS - Sale #{sale_id} Details")
        dialog.resize(700, 400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        
        header_label = QLabel(f"Sale #{sale_id} - Item Details")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background-color: #f0f0f0; border: 2px solid #ccc;")
        layout.addWidget(header_label)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Quantity", "Unit Price", "Line Total"
        ])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("border: 2px solid #ccc;")
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT product_id, product_name, quantity, unit_price, line_total, milliliters
                FROM sale_items
                WHERE sale_id = ?
                ORDER BY id
            """, (sale_id,))
            
            items = cursor.fetchall()
            table.setRowCount(len(items))
            
            for row_idx, item in enumerate(items):
                # Convert sqlite3.Row to dict if needed
                if hasattr(item, 'keys'):
                    item_dict = dict(item)
                else:
                    item_dict = item
                
                table.setItem(row_idx, 0, QTableWidgetItem(item_dict['product_id']))
                table.setItem(row_idx, 1, QTableWidgetItem(item_dict['product_name']))
                # Handle milliliters - may not exist in older databases
                try:
                    mls = item_dict['milliliters'] if item_dict.get('milliliters') is not None else 0
                except (KeyError, TypeError):
                    mls = 0
                mls_str = f"{mls}ml" if mls > 0 else "-"
                table.setItem(row_idx, 2, QTableWidgetItem(mls_str))
                table.setItem(row_idx, 3, QTableWidgetItem(str(item_dict['quantity'])))
                table.setItem(row_idx, 4, QTableWidgetItem(format_currency(item_dict['unit_price'])))
                table.setItem(row_idx, 5, QTableWidgetItem(format_currency(item_dict['line_total'])))
            
            table.resizeColumnsToContents()
        finally:
            conn.close()
        
        layout.addWidget(table)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                padding: 8px 20px;
                border-radius: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()

