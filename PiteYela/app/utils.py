"""
Shared utility functions for Alcohol POS System.
Date utilities, currency formatting, validation, and error dialogs.
"""
from datetime import datetime, timedelta
from typing import Optional
from PyQt6.QtWidgets import QMessageBox

def format_currency(amount: float) -> str:
    """Format amount as currency string (Uganda Shillings)."""
    return f"UGX {amount:,.0f}"

def format_date(date: datetime) -> str:
    """Format date as string."""
    return date.strftime("%Y-%m-%d")

def format_datetime(dt: datetime) -> str:
    """Format datetime as string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def get_date_range(period: str) -> tuple[datetime, datetime]:
    """
    Get date range for a period.
    
    Args:
        period: 'day', 'week', 'month', or 'year'
        
    Returns:
        (start_date, end_date)
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    
    if period == 'day':
        start_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
    elif period == 'month':
        start_date = today.replace(day=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today
    
    return start_date, end_date

def validate_product_id(product_id: str) -> tuple[bool, str]:
    """Validate product ID format."""
    if not product_id or not product_id.strip():
        return False, "Product ID cannot be empty"
    if len(product_id.strip()) > 50:
        return False, "Product ID too long (max 50 characters)"
    return True, ""

def validate_price(price: float) -> tuple[bool, str]:
    """Validate price value."""
    if price < 0:
        return False, "Price cannot be negative"
    if price > 999999.99:
        return False, "Price too large"
    return True, ""

def validate_quantity(quantity: int) -> tuple[bool, str]:
    """Validate quantity value."""
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    if quantity > 9999:
        return False, "Quantity too large"
    return True, ""

def show_error_dialog(parent, title: str, message: str):
    """Show error dialog."""
    QMessageBox.critical(parent, title, message)

def show_info_dialog(parent, title: str, message: str):
    """Show info dialog."""
    QMessageBox.information(parent, title, message)

def show_warning_dialog(parent, title: str, message: str):
    """Show warning dialog."""
    QMessageBox.warning(parent, title, message)

def show_question_dialog(parent, title: str, message: str) -> bool:
    """Show question dialog. Returns True if Yes, False if No."""
    reply = QMessageBox.question(parent, title, message, 
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return reply == QMessageBox.StandardButton.Yes

