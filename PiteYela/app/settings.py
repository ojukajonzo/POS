"""
Settings and configuration module for Alcohol POS System.
Handles printer configuration, barcode scanner settings, and system preferences.
"""
import json
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QComboBox,
                             QGroupBox, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from app.config import BASE_DIR
from app.auth import is_admin
from app.utils import show_error_dialog, show_info_dialog

SETTINGS_FILE = BASE_DIR / "settings.json"

def load_settings() -> Dict:
    """Load settings from file."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return get_default_settings()

def save_settings(settings: Dict) -> bool:
    """Save settings to file."""
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def get_default_settings() -> Dict:
    """Get default settings."""
    return {
        "printer": {
            "type": "file",
            "usb_vendor_id": "",
            "usb_product_id": "",
            "serial_port": "COM1",
            "baudrate": 9600
        },
        "barcode": {
            "scanner_type": "keyboard",
            "suffix": "\n",
            "prefix": ""
        },
        "shop": {
            "name": "Alcohol POS Store",
            "address": "",
            "phone": "",
            "email": ""
        }
    }

class SettingsWindow(QWidget):
    """Settings configuration window (Admin only)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if not is_admin():
            show_error_dialog(self, "Access Denied", "Admin access required")
            return
        
        self.setWindowTitle("PiteYelaHouseofWine_POS - System Settings")
        self.resize(600, 500)
        self.setStyleSheet("background-color: white;")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        
        self.settings = load_settings()
        
        layout = QVBoxLayout()
        
        # Back button
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.close)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        # Tabs
        tabs = QTabWidget()
        
        # Printer settings tab
        printer_tab = self.create_printer_tab()
        tabs.addTab(printer_tab, "Printer")
        
        # Barcode scanner tab
        barcode_tab = self.create_barcode_tab()
        tabs.addTab(barcode_tab, "Barcode Scanner")
        
        # Shop info tab
        shop_tab = self.create_shop_tab()
        tabs.addTab(shop_tab, "Shop Information")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_all_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
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
        self.save_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_printer_tab(self) -> QWidget:
        """Create printer settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        self.printer_type_combo = QComboBox()
        self.printer_type_combo.addItems(["file", "usb", "serial"])
        self.printer_type_combo.setCurrentText(self.settings.get("printer", {}).get("type", "file"))
        layout.addRow("Printer Type:", self.printer_type_combo)
        
        self.usb_vendor_input = QLineEdit()
        self.usb_vendor_input.setText(self.settings.get("printer", {}).get("usb_vendor_id", ""))
        self.usb_vendor_input.setPlaceholderText("e.g., 0x04f9")
        layout.addRow("USB Vendor ID:", self.usb_vendor_input)
        
        self.usb_product_input = QLineEdit()
        self.usb_product_input.setText(self.settings.get("printer", {}).get("usb_product_id", ""))
        self.usb_product_input.setPlaceholderText("e.g., 0x2016")
        layout.addRow("USB Product ID:", self.usb_product_input)
        
        self.serial_port_input = QLineEdit()
        self.serial_port_input.setText(self.settings.get("printer", {}).get("serial_port", "COM1"))
        layout.addRow("Serial Port:", self.serial_port_input)
        
        self.baudrate_input = QLineEdit()
        self.baudrate_input.setText(str(self.settings.get("printer", {}).get("baudrate", 9600)))
        layout.addRow("Baudrate:", self.baudrate_input)
        
        widget.setLayout(layout)
        return widget
    
    def create_barcode_tab(self) -> QWidget:
        """Create barcode scanner settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        self.scanner_type_combo = QComboBox()
        self.scanner_type_combo.addItems(["keyboard", "serial"])
        self.scanner_type_combo.setCurrentText(self.settings.get("barcode", {}).get("scanner_type", "keyboard"))
        layout.addRow("Scanner Type:", self.scanner_type_combo)
        
        self.barcode_prefix_input = QLineEdit()
        self.barcode_prefix_input.setText(self.settings.get("barcode", {}).get("prefix", ""))
        layout.addRow("Barcode Prefix:", self.barcode_prefix_input)
        
        self.barcode_suffix_input = QLineEdit()
        self.barcode_suffix_input.setText(self.settings.get("barcode", {}).get("suffix", "\n"))
        layout.addRow("Barcode Suffix:", self.barcode_suffix_input)
        
        info_label = QLabel("Note: Most barcode scanners work as keyboard input.\nSuffix is usually 'Enter' key (\\n)")
        info_label.setWordWrap(True)
        layout.addRow("", info_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_shop_tab(self) -> QWidget:
        """Create shop information tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        self.shop_name_input = QLineEdit()
        self.shop_name_input.setText(self.settings.get("shop", {}).get("name", "Alcohol POS Store"))
        layout.addRow("Shop Name:", self.shop_name_input)
        
        self.shop_address_input = QLineEdit()
        self.shop_address_input.setText(self.settings.get("shop", {}).get("address", ""))
        layout.addRow("Address:", self.shop_address_input)
        
        self.shop_phone_input = QLineEdit()
        self.shop_phone_input.setText(self.settings.get("shop", {}).get("phone", ""))
        layout.addRow("Phone:", self.shop_phone_input)
        
        self.shop_email_input = QLineEdit()
        self.shop_email_input.setText(self.settings.get("shop", {}).get("email", ""))
        layout.addRow("Email:", self.shop_email_input)
        
        widget.setLayout(layout)
        return widget
    
    def save_all_settings(self):
        """Save all settings."""
        # Update settings dict
        self.settings["printer"] = {
            "type": self.printer_type_combo.currentText(),
            "usb_vendor_id": self.usb_vendor_input.text().strip(),
            "usb_product_id": self.usb_product_input.text().strip(),
            "serial_port": self.serial_port_input.text().strip(),
            "baudrate": int(self.baudrate_input.text()) if self.baudrate_input.text().isdigit() else 9600
        }
        
        self.settings["barcode"] = {
            "scanner_type": self.scanner_type_combo.currentText(),
            "prefix": self.barcode_prefix_input.text(),
            "suffix": self.barcode_suffix_input.text()
        }
        
        self.settings["shop"] = {
            "name": self.shop_name_input.text().strip(),
            "address": self.shop_address_input.text().strip(),
            "phone": self.shop_phone_input.text().strip(),
            "email": self.shop_email_input.text().strip()
        }
        
        if save_settings(self.settings):
            show_info_dialog(self, "Success", "Settings saved successfully!")
            self.close()
        else:
            show_error_dialog(self, "Error", "Failed to save settings")

