"""
Backup and restore module for Alcohol POS System.
Handles database backup and restore functionality.
"""
import shutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QFileDialog, QMessageBox, QGroupBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from app.config import DB_PATH, BASE_DIR
from app.auth import is_admin
from app.utils import show_error_dialog, show_info_dialog

BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def create_backup() -> tuple[bool, str]:
    """Create a backup of the database."""
    try:
        if not DB_PATH.exists():
            return False, "Database file not found"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pos_backup_{timestamp}.db"
        backup_path = BACKUP_DIR / backup_filename
        
        shutil.copy2(DB_PATH, backup_path)
        return True, str(backup_path)
    except Exception as e:
        return False, str(e)

def restore_backup(backup_path: str) -> tuple[bool, str]:
    """Restore database from backup."""
    try:
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return False, "Backup file not found"
        
        # Create a backup of current database before restoring
        if DB_PATH.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = BACKUP_DIR / f"pre_restore_{timestamp}.db"
            shutil.copy2(DB_PATH, safety_backup)
        
        # Restore
        shutil.copy2(backup_file, DB_PATH)
        return True, "Database restored successfully"
    except Exception as e:
        return False, str(e)

class BackupWindow(QWidget):
    """Backup and restore window (Admin only)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if not is_admin():
            show_error_dialog(self, "Access Denied", "Admin access required")
            return
        
        self.setWindowTitle("PiteYelaHouseofWine_POS - Backup & Restore")
        self.resize(500, 300)
        self.setStyleSheet("background-color: white;")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        
        layout = QVBoxLayout()
        
        # Back button
        back_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.close)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                padding: 8px 16px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                border: 2px solid #45a049;
            }
        """)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        # Backup section
        backup_group = QGroupBox("Database Backup")
        backup_layout = QVBoxLayout()
        
        info_label = QLabel("Create a backup of your database. Backups are stored in:\n" + str(BACKUP_DIR))
        info_label.setWordWrap(True)
        backup_layout.addWidget(info_label)
        
        self.backup_btn = QPushButton("Create Backup Now")
        self.backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(self.backup_btn)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Restore section
        restore_group = QGroupBox("Restore Database")
        restore_group.setStyleSheet("""
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
        restore_layout = QVBoxLayout()
        
        warning_label = QLabel("⚠️ WARNING: Restoring will replace your current database!\nA backup will be created automatically before restore.")
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: red; font-weight: bold; padding: 10px; background-color: #ffebee; border: 2px solid #f44336;")
        restore_layout.addWidget(warning_label)
        
        self.restore_btn = QPushButton("Restore from Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setStyleSheet("""
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
        """)
        restore_layout.addWidget(self.restore_btn)
        
        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_backup(self):
        """Create a backup."""
        reply = QMessageBox.question(
            self, "Create Backup",
            "Create a backup of the database now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = create_backup()
            if success:
                show_info_dialog(self, "Backup Created", f"Backup created successfully!\n\nLocation: {message}")
            else:
                show_error_dialog(self, "Backup Failed", f"Failed to create backup:\n{message}")
    
    def restore_backup(self):
        """Restore from backup."""
        reply = QMessageBox.warning(
            self, "Confirm Restore",
            "⚠️ WARNING: This will replace your current database!\n\nA backup of the current database will be created first.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", str(BACKUP_DIR), "Database Files (*.db)"
            )
            
            if filename:
                success, message = restore_backup(filename)
                if success:
                    show_info_dialog(self, "Restore Complete", 
                                   f"{message}\n\nPlease restart the application for changes to take effect.")
                else:
                    show_error_dialog(self, "Restore Failed", f"Failed to restore backup:\n{message}")

