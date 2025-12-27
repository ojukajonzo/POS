"""
Inventory management module for Alcohol POS System.
Admin-only product and stock management.
"""
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                             QDialog, QFormLayout, QDoubleSpinBox, QSpinBox,
                             QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from app.database import get_connection, execute_transaction
from app.models import Product, get_product
from app.auth import is_admin, require_admin
from app.utils import format_currency, validate_product_id, validate_price, validate_quantity, show_error_dialog

class ProductDialog(QDialog):
    """Dialog for adding/editing products."""
    
    def __init__(self, parent=None, product_id: Optional[str] = None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("PiteYelaHouseofWine_POS - " + ("Add Product" if not product_id else "Edit Product"))
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QFormLayout()
        
        # Product ID
        self.id_input = QLineEdit()
        self.id_input.setMaxLength(50)
        if product_id:
            self.id_input.setText(product_id)
            self.id_input.setReadOnly(True)  # Can't change ID when editing
        layout.addRow("Product ID:", self.id_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(200)
        layout.addRow("Product Name:", self.name_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)
        
        # Milliliters
        self.milliliters_input = QSpinBox()
        self.milliliters_input.setMaximum(99999)
        self.milliliters_input.setMinimum(0)
        self.milliliters_input.setSuffix(" ml")
        layout.addRow("Milliliters:", self.milliliters_input)
        
        # Cost Price
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setMaximum(999999999.99)
        self.cost_price_input.setDecimals(0)
        self.cost_price_input.setPrefix("UGX ")
        layout.addRow("Cost Price:", self.cost_price_input)
        
        # Selling Price
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setMaximum(999999999.99)
        self.selling_price_input.setDecimals(0)
        self.selling_price_input.setPrefix("UGX ")
        layout.addRow("Selling Price:", self.selling_price_input)
        
        # Quantity Stocked
        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setMinimum(0)
        layout.addRow("Quantity to Stock:", self.quantity_input)
        
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
        
        # Load existing product if editing
        if product_id:
            self.load_product()
        
        # Connect signals
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_product(self):
        """Load product data into form."""
        product = get_product(self.product_id)
        if product:
            self.name_input.setText(product.name)
            self.description_input.setPlainText(product.description)
            self.milliliters_input.setValue(product.milliliters)
            self.cost_price_input.setValue(product.cost_price)
            self.selling_price_input.setValue(product.selling_price)
            self.quantity_input.setValue(product.quantity_stocked)
    
    def get_data(self) -> Dict:
        """Get form data."""
        return {
            'id': self.id_input.text().strip(),
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'milliliters': self.milliliters_input.value(),
            'cost_price': self.cost_price_input.value(),
            'selling_price': self.selling_price_input.value(),
            'quantity_stocked': self.quantity_input.value()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate form data."""
        data = self.get_data()
        
        # Validate ID
        valid, msg = validate_product_id(data['id'])
        if not valid:
            return False, msg
        
        # Validate name
        if not data['name']:
            return False, "Product name is required"
        
        # Validate prices
        valid, msg = validate_price(data['cost_price'])
        if not valid:
            return False, msg
        
        valid, msg = validate_price(data['selling_price'])
        if not valid:
            return False, msg
        
        if data['selling_price'] < data['cost_price']:
            return False, "Selling price should be >= cost price"
        
        # Validate quantity
        valid, msg = validate_quantity(data['quantity_stocked'])
        if not valid and data['quantity_stocked'] > 0:
            return False, msg
        
        return True, ""

class InventoryWindow(QWidget):
    """Inventory management window (Admin only)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if not is_admin():
            show_error_dialog(self, "Access Denied", "Admin access required")
            return
        
        self.setWindowTitle("PiteYelaHouseofWine_POS - Inventory Management")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.close)
        self.add_btn = QPushButton("Add Product")
        self.edit_btn = QPushButton("Edit Product")
        self.delete_btn = QPushButton("Delete Product")
        self.refresh_btn = QPushButton("Refresh")
        
        # Apply button styles
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
        for btn in [self.back_btn, self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            btn.setStyleSheet(button_style)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "MLs", "Cost Price", "Selling Price", "Profit",
            "Stocked", "Sold", "Available", "Description"
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
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.refresh_btn.clicked.connect(self.refresh_table)
        
        # Load data
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh product table."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, milliliters, cost_price, selling_price, profit,
                       quantity_stocked, quantity_sold, quantity_available
                FROM products
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))
            
            for row_idx, row in enumerate(rows):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(row['name']))
                # Handle milliliters - may not exist in older databases
                try:
                    mls = row['milliliters'] if row['milliliters'] is not None else 0
                except (KeyError, IndexError):
                    mls = 0
                mls_str = f"{mls} ml" if mls > 0 else "-"
                self.table.setItem(row_idx, 2, QTableWidgetItem(mls_str))
                self.table.setItem(row_idx, 3, QTableWidgetItem(format_currency(row['cost_price'])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(format_currency(row['selling_price'])))
                self.table.setItem(row_idx, 5, QTableWidgetItem(format_currency(row['profit'])))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(row['quantity_stocked'])))
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(row['quantity_sold'])))
                self.table.setItem(row_idx, 8, QTableWidgetItem(str(row['quantity_available'])))
                self.table.setItem(row_idx, 9, QTableWidgetItem(row['description'] or ""))
            
            self.table.resizeColumnsToContents()
        finally:
            conn.close()
    
    def add_product(self):
        """Open dialog to add new product."""
        dialog = ProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            valid, msg = dialog.validate()
            if not valid:
                show_error_dialog(self, "Validation Error", msg)
                return
            
            # Calculate profit
            profit = data['selling_price'] - data['cost_price']
            
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (id, name, description, milliliters, cost_price, selling_price, profit,
                                        quantity_stocked, quantity_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['id'], data['name'], data['description'], data['milliliters'],
                      data['cost_price'], data['selling_price'], profit, 
                      data['quantity_stocked'], data['quantity_stocked']))
                conn.commit()
                self.refresh_table()
                QMessageBox.information(self, "Success", "Product added successfully")
            except Exception as e:
                show_error_dialog(self, "Error", f"Failed to add product: {str(e)}")
            finally:
                conn.close()
    
    def edit_product(self):
        """Edit selected product."""
        selected = self.table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select a product to edit")
            return
        
        product_id = self.table.item(selected[0].row(), 0).text()
        dialog = ProductDialog(self, product_id)
        
        if dialog.exec():
            data = dialog.get_data()
            valid, msg = dialog.validate()
            if not valid:
                show_error_dialog(self, "Validation Error", msg)
                return
            
            # Calculate profit
            profit = data['selling_price'] - data['cost_price']
            
            # Get current quantity_sold to calculate new quantity_available
            product = get_product(product_id)
            if not product:
                show_error_dialog(self, "Error", "Product not found")
                return
            
            new_quantity_available = data['quantity_stocked'] - product.quantity_sold
            if new_quantity_available < 0:
                show_error_dialog(self, "Error", "Cannot reduce stock below sold quantity")
                return
            
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE products
                    SET name = ?, description = ?, milliliters = ?, cost_price = ?, selling_price = ?,
                        profit = ?, quantity_stocked = ?, quantity_available = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (data['name'], data['description'], data['milliliters'], data['cost_price'],
                      data['selling_price'], profit, data['quantity_stocked'],
                      new_quantity_available, product_id))
                conn.commit()
                self.refresh_table()
                QMessageBox.information(self, "Success", "Product updated successfully")
            except Exception as e:
                show_error_dialog(self, "Error", f"Failed to update product: {str(e)}")
            finally:
                conn.close()
    
    def delete_product(self):
        """Delete selected product."""
        selected = self.table.selectedItems()
        if not selected:
            show_error_dialog(self, "No Selection", "Please select a product to delete")
            return
        
        product_id = self.table.item(selected[0].row(), 0).text()
        product_name = self.table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                self.refresh_table()
                QMessageBox.information(self, "Success", "Product deleted successfully")
            except Exception as e:
                show_error_dialog(self, "Error", f"Failed to delete product: {str(e)}")
            finally:
                conn.close()

