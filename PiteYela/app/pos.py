"""
Point of Sale (POS) interface for Alcohol POS System.
Main screen for processing sales, scanning products, and printing receipts.
"""
from typing import List, Dict, Optional
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QSpinBox, QMessageBox, QGroupBox, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from app.models import get_product, validate_stock_availability, calculate_line_total, calculate_grand_total, create_sale
from app.auth import get_current_user, is_admin
from app.printer import print_receipt, reprint_last_receipt
from app.utils import format_currency, show_error_dialog, show_info_dialog, show_question_dialog
from app.config import SHOP_NAME, RECEIPT_ALCOHOL_WARNING

class POSWindow(QWidget):
    """Main POS interface window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PiteYelaHouseofWine_POS - Point of Sale")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: white;")
        
        # Cart data
        self.cart: List[Dict] = []
        self.current_product_id = ""
        self.current_quantity = 1
        
        # Layout
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        user = get_current_user()
        self.user_label = QLabel(f"Cashier: {user['full_name'] if user else 'Unknown'}")
        self.user_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.user_label)
        header_layout.addStretch()
        
        # Password change button (all users)
        self.password_btn = QPushButton("Change Password")
        self.password_btn.clicked.connect(self.change_password)
        header_layout.addWidget(self.password_btn)
        
        if is_admin():
            self.admin_menu_btn = QPushButton("Admin Menu")
            self.admin_menu_btn.clicked.connect(self.show_admin_menu)
            header_layout.addWidget(self.admin_menu_btn)
        
        main_layout.addLayout(header_layout)
        
        # Product input section
        input_group = QGroupBox("Product Entry")
        input_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #ccc;
                border-radius: 0px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
        """)
        input_layout = QVBoxLayout()
        
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Product ID / Barcode:"))
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("Scan or type product ID, then press Enter")
        self.product_id_input.returnPressed.connect(self.on_product_id_entered)
        self.product_id_input.setFocus()
        product_layout.addWidget(self.product_id_input)
        input_layout.addLayout(product_layout)
        
        # Product details (auto-filled)
        details_layout = QHBoxLayout()
        self.product_name_label = QLabel("Product: -")
        self.product_price_label = QLabel("Price: -")
        details_layout.addWidget(self.product_name_label)
        details_layout.addWidget(self.product_price_label)
        details_layout.addStretch()
        input_layout.addLayout(details_layout)
        
        # Quantity and add button
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999)
        self.quantity_input.setValue(1)
        quantity_layout.addWidget(self.quantity_input)
        
        self.next_item_btn = QPushButton("Next Item")
        self.next_item_btn.clicked.connect(self.add_item_to_cart)
        self.next_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                font-weight: bold;
                padding: 8px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                border: 2px solid #45a049;
            }
        """)
        quantity_layout.addWidget(self.next_item_btn)
        quantity_layout.addStretch()
        input_layout.addLayout(quantity_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Cart section
        cart_group = QGroupBox("Cart / Sale List")
        cart_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #ccc;
                border-radius: 0px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
        """)
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "Product", "Quantity", "Unit Price", "Line Total", "Action"
        ])
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        cart_layout.addWidget(self.cart_table)
        
        # Cart total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel("Grand Total: UGX 0")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        total_layout.addWidget(self.total_label)
        cart_layout.addLayout(total_layout)
        
        cart_group.setLayout(cart_layout)
        main_layout.addWidget(cart_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.remove_item_btn = QPushButton("Remove Selected Item")
        self.remove_item_btn.clicked.connect(self.remove_selected_item)
        self.remove_item_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                padding: 8px 16px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """)
        button_layout.addWidget(self.remove_item_btn)
        
        self.cancel_sale_btn = QPushButton("Cancel Sale")
        self.cancel_sale_btn.clicked.connect(self.cancel_sale)
        self.cancel_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """)
        button_layout.addWidget(self.cancel_sale_btn)
        
        button_layout.addStretch()
        
        self.complete_sale_btn = QPushButton("Complete Sale")
        self.complete_sale_btn.clicked.connect(self.complete_sale)
        self.complete_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid #000000;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #000000;
            }
        """)
        button_layout.addWidget(self.complete_sale_btn)
        
        main_layout.addLayout(button_layout)
        
        # Receipt buttons (for admin)
        if is_admin():
            receipt_layout = QHBoxLayout()
            receipt_layout.addStretch()
            self.reprint_btn = QPushButton("Reprint Last Receipt")
            self.reprint_btn.clicked.connect(self.reprint_receipt)
            receipt_layout.addWidget(self.reprint_btn)
            main_layout.addLayout(receipt_layout)
        
        self.setLayout(main_layout)
        
        # Auto-focus on product ID input
        QTimer.singleShot(100, self.product_id_input.setFocus)
    
    def on_product_id_entered(self):
        """Handle product ID entry (Enter key or barcode scan)."""
        product_id = self.product_id_input.text().strip()
        if not product_id:
            return
        
        product = get_product(product_id)
        if not product:
            show_error_dialog(self, "Product Not Found", f"Product ID '{product_id}' not found in inventory.")
            self.product_id_input.clear()
            self.product_id_input.setFocus()
            return
        
        # Check stock availability
        quantity = self.quantity_input.value()
        valid, msg = validate_stock_availability(product_id, quantity)
        if not valid:
            show_error_dialog(self, "Stock Error", msg)
            self.product_id_input.clear()
            self.product_id_input.setFocus()
            return
        
        # Auto-fill product details
        self.product_name_label.setText(f"Product: {product.name}")
        self.product_price_label.setText(f"Price: {format_currency(product.selling_price)}")
        self.current_product_id = product_id
        self.current_quantity = quantity
        
        # Auto-add to cart (optional - user can adjust quantity first)
        # For now, just show the product and let user click "Next Item"
    
    def add_item_to_cart(self):
        """Add current item to cart."""
        if not self.current_product_id:
            show_error_dialog(self, "No Product", "Please enter a product ID first.")
            return
        
        product = get_product(self.current_product_id)
        if not product:
            show_error_dialog(self, "Error", "Product not found.")
            return
        
        quantity = self.quantity_input.value()
        
        # Validate stock
        valid, msg = validate_stock_availability(self.current_product_id, quantity)
        if not valid:
            show_error_dialog(self, "Stock Error", msg)
            return
        
        # Check if product already in cart
        existing_item = None
        for item in self.cart:
            if item['product_id'] == self.current_product_id:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            valid, msg = validate_stock_availability(self.current_product_id, new_quantity)
            if not valid:
                show_error_dialog(self, "Stock Error", f"Cannot add {quantity} more. {msg}")
                return
            existing_item['quantity'] = new_quantity
            existing_item['line_total'] = calculate_line_total(existing_item['unit_price'], existing_item['quantity'])
        else:
            # Add new item
            line_total = calculate_line_total(product.selling_price, quantity)
            self.cart.append({
                'product_id': self.current_product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': product.selling_price,
                'line_total': line_total
            })
        
        # Clear input and refresh
        self.product_id_input.clear()
        self.product_name_label.setText("Product: -")
        self.product_price_label.setText("Price: -")
        self.current_product_id = ""
        self.quantity_input.setValue(1)
        self.refresh_cart()
        self.product_id_input.setFocus()
    
    def remove_selected_item(self):
        """Remove selected item from cart."""
        selected = self.cart_table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select an item to remove.")
            return
        
        row = selected[0].row()
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.refresh_cart()
    
    def cancel_sale(self):
        """Cancel current sale and clear cart."""
        if not self.cart:
            return
        
        if show_question_dialog(self, "Cancel Sale", "Are you sure you want to cancel this sale?"):
            self.cart.clear()
            self.refresh_cart()
            self.product_id_input.clear()
            self.product_id_input.setFocus()
    
    def complete_sale(self):
        """Complete the sale and process payment."""
        if not self.cart:
            show_error_dialog(self, "Empty Cart", "Cannot complete sale with empty cart.")
            return
        
        # Validate all items have stock
        for item in self.cart:
            valid, msg = validate_stock_availability(item['product_id'], item['quantity'])
            if not valid:
                show_error_dialog(self, "Stock Error", f"{item['product_name']}: {msg}")
                return
        
        user = get_current_user()
        if not user:
            show_error_dialog(self, "Error", "User session expired. Please login again.")
            return
        
        # Create sale in database
        sale_id = create_sale(
            cashier_id=user['id'],
            cashier_name=user['full_name'],
            items=self.cart
        )
        
        if not sale_id:
            show_error_dialog(self, "Error", "Failed to create sale. Please try again.")
            return
        
        # Clear cart immediately for faster response
        self.cart.clear()
        self.refresh_cart()
        self.product_id_input.clear()
        self.product_id_input.setFocus()
        
        # Show success message immediately
        show_info_dialog(self, "Sale Complete", f"Sale #{sale_id} completed successfully!")
        
        # Print receipt in background (non-blocking)
        try:
            from app.models import get_sale_details
            from app.settings import load_settings
            
            sale_data = get_sale_details(sale_id)
            if sale_data:
                settings = load_settings()
                printer_type = settings.get("printer", {}).get("type", "file")
                # Print in a background thread to avoid blocking the UI
                import threading

                def _print_async(data, ptype):
                    try:
                        print_receipt(data, printer_type=ptype)
                    except Exception as _e:
                        print(f"Receipt printing error (background): {_e}")

                threading.Thread(target=_print_async, args=(sale_data, printer_type), daemon=True).start()
        except Exception as e:
            # Don't block on receipt printing errors
            print(f"Receipt printing error: {e}")
    
    def reprint_receipt(self):
        """Reprint last receipt (Admin only)."""
        success, msg = reprint_last_receipt()
        if success:
            show_info_dialog(self, "Reprint", f"Last receipt reprinted successfully!\n\n{msg}")
        else:
            show_error_dialog(self, "Reprint Failed", msg)
    
    def refresh_cart(self):
        """Refresh cart table display."""
        self.cart_table.setRowCount(len(self.cart))
        
        for row_idx, item in enumerate(self.cart):
            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(item['product_name']))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row_idx, 2, QTableWidgetItem(format_currency(item['unit_price'])))
            self.cart_table.setItem(row_idx, 3, QTableWidgetItem(format_currency(item['line_total'])))
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 2px solid #000000;
                    padding: 5px 10px;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    border: 2px solid #000000;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row_idx: self.remove_item_at_row(r))
            self.cart_table.setCellWidget(row_idx, 4, remove_btn)
        
        # Update total
        grand_total = calculate_grand_total(self.cart)
        self.total_label.setText(f"Grand Total: {format_currency(grand_total)}")
        
        self.cart_table.resizeColumnsToContents()
    
    def remove_item_at_row(self, row: int):
        """Remove item at specific row."""
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self.refresh_cart()
    
    def show_admin_menu(self):
        """Show admin menu with all admin options."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        inventory_action = menu.addAction("Inventory Management")
        reports_action = menu.addAction("Sales Reports")
        users_action = menu.addAction("User Management")
        settings_action = menu.addAction("Settings")
        backup_action = menu.addAction("Backup & Restore")
        menu.addSeparator()
        password_action = menu.addAction("Change Password")
        
        action = menu.exec(self.admin_menu_btn.mapToGlobal(self.admin_menu_btn.rect().bottomLeft()))
        
        if action == inventory_action:
            from app.inventory import InventoryWindow
            self.inventory_window = InventoryWindow()
            self.inventory_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.inventory_window.show()
        elif action == reports_action:
            from app.reports import ReportsWindow
            self.reports_window = ReportsWindow()
            self.reports_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.reports_window.show()
        elif action == users_action:
            from app.users import UsersWindow
            self.users_window = UsersWindow()
            self.users_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.users_window.show()
        elif action == settings_action:
            from app.settings import SettingsWindow
            self.settings_window = SettingsWindow()
            self.settings_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.settings_window.show()
        elif action == backup_action:
            from app.backup import BackupWindow
            self.backup_window = BackupWindow()
            self.backup_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.backup_window.show()
        elif action == password_action:
            from app.password import PasswordChangeDialog
            dialog = PasswordChangeDialog(self)
            dialog.exec()
    
    def change_password(self):
        """Show password change dialog."""
        from app.password import PasswordChangeDialog
        dialog = PasswordChangeDialog(self)
        dialog.exec()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_sale()
        elif event.key() == Qt.Key.Key_F1 and is_admin():
            self.show_admin_menu()
        else:
            super().keyPressEvent(event)

