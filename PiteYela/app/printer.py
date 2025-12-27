"""
Receipt printing module for Alcohol POS System.
Handles ESC/POS printer communication and receipt formatting.
"""
from datetime import datetime
from typing import List, Dict, Optional
from app.config import SHOP_NAME, SHOP_DISPLAY_NAME, SHOP_LOCATION, SHOP_CONTACT, RECEIPT_ALCOHOL_WARNING
from app.utils import format_currency, format_datetime

try:
    from escpos.printer import Usb, Serial, File
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    print("Warning: python-escpos not available. Printing will use file output.")

_last_receipt_data: Optional[Dict] = None

def format_receipt_text(sale_data: Dict) -> str:
    """
    Format receipt as text string.
    
    Args:
        sale_data: Dict with keys: sale_id, cashier_name, sale_date, grand_total, items
        
    Returns:
        Formatted receipt text
    """
    lines = []
    lines.append("=" * 50)
    lines.append(f"  {SHOP_DISPLAY_NAME}")
    lines.append(f"  Location: {SHOP_LOCATION}")
    lines.append(f"  Contact: {SHOP_CONTACT}")
    lines.append("=" * 50)
    # Parse sale_date (handle both string and datetime)
    sale_date_str = sale_data['sale_date']
    if isinstance(sale_date_str, str):
        try:
            # Try parsing ISO format
            if 'T' in sale_date_str:
                sale_dt = datetime.fromisoformat(sale_date_str.replace('Z', '+00:00'))
            else:
                sale_dt = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
        except:
            sale_dt = datetime.now()
    else:
        sale_dt = sale_date_str if isinstance(sale_date_str, datetime) else datetime.now()
    
    lines.append(f"Date: {format_datetime(sale_dt)}")
    lines.append(f"Cashier: {sale_data['cashier_name']}")
    lines.append(f"Receipt #: {sale_data['sale_id']}")
    lines.append("-" * 50)
    lines.append(f"{'Item':<20} {'MLs':>6} {'Qty':>5} {'Price':>10} {'Total':>10}")
    lines.append("-" * 50)
    
    for item in sale_data['items']:
        name = item['product_name'][:20]  # Truncate long names
        # Handle milliliters - may not exist in older databases
        try:
            mls = item['milliliters'] if item.get('milliliters') is not None else 0
        except (KeyError, TypeError):
            mls = 0
        mls_str = f"{mls}ml" if mls > 0 else "-"
        qty = item['quantity']
        price = format_currency(item['unit_price'])
        total = format_currency(item['line_total'])
        lines.append(f"{name:<20} {mls_str:>6} {qty:>5} {price:>10} {total:>10}")
    
    lines.append("-" * 40)
    lines.append(f"{'GRAND TOTAL:':<30} {format_currency(sale_data['grand_total']):>10}")
    lines.append("=" * 40)
    lines.append("")
    lines.append(RECEIPT_ALCOHOL_WARNING)
    lines.append("")
    lines.append("Thank you for your purchase!")
    lines.append("=" * 40)
    
    return "\n".join(lines)

def print_receipt(sale_data: Dict, printer_type: str = None) -> tuple[bool, str]:
    """
    Print receipt to printer.
    
    Args:
        sale_data: Sale data dictionary
        printer_type: 'usb', 'serial', or 'file' (if None, uses settings)
        
    Returns:
        (success, error_message)
    """
    global _last_receipt_data
    _last_receipt_data = sale_data
    
    # Load printer type from settings if not provided
    if printer_type is None:
        from app.settings import load_settings
        settings = load_settings()
        printer_type = settings.get("printer", {}).get("type", "file")
    
    if not ESCPOS_AVAILABLE:
        # Fallback to file printing
        return print_to_file(sale_data)
    
    try:
        receipt_text = format_receipt_text(sale_data)
        
        if printer_type == "file":
            return print_to_file(sale_data)
        elif printer_type == "usb":
            # Try USB printer
            from app.settings import load_settings
            settings = load_settings()
            vendor_id = settings.get("printer", {}).get("usb_vendor_id", "")
            product_id = settings.get("printer", {}).get("usb_product_id", "")
            
            if vendor_id and product_id:
                try:
                    vendor_id_int = int(vendor_id, 16) if vendor_id.startswith('0x') else int(vendor_id)
                    product_id_int = int(product_id, 16) if product_id.startswith('0x') else int(product_id)
                    printer = Usb(vendor_id_int, product_id_int)
                    printer.text(receipt_text)
                    printer.cut()
                    return True, "Receipt printed to USB printer"
                except Exception as e:
                    return print_to_file(sale_data)  # Fallback to file
            else:
                return print_to_file(sale_data)  # Fallback to file
        elif printer_type == "serial":
            # Try serial printer
            from app.settings import load_settings
            settings = load_settings()
            port = settings.get("printer", {}).get("serial_port", "COM1")
            baudrate = settings.get("printer", {}).get("baudrate", 9600)
            
            try:
                printer = Serial(port=port, baudrate=baudrate)
                printer.text(receipt_text)
                printer.cut()
                return True, f"Receipt printed to serial printer ({port})"
            except Exception as e:
                return print_to_file(sale_data)  # Fallback to file
        else:
            return print_to_file(sale_data)
            
    except Exception as e:
        return False, f"Print error: {str(e)}"

def print_to_file(sale_data: Dict) -> tuple[bool, str]:
    """Print receipt to file (fallback method)."""
    try:
        from app.config import BASE_DIR
        from pathlib import Path
        
        receipt_text = format_receipt_text(sale_data)
        receipt_dir = BASE_DIR / "receipts"
        receipt_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        receipt_file = receipt_dir / f"receipt_{sale_data['sale_id']}_{timestamp}.txt"
        
        with open(receipt_file, 'w', encoding='utf-8') as f:
            f.write(receipt_text)
        
        return True, f"Receipt saved to: {receipt_file}"
    except Exception as e:
        return False, f"File print error: {str(e)}"

def reprint_last_receipt() -> tuple[bool, str]:
    """Reprint the last receipt (Admin only)."""
    if _last_receipt_data is None:
        return False, "No receipt to reprint"
    
    return print_receipt(_last_receipt_data)

def get_last_receipt_data() -> Optional[Dict]:
    """Get last receipt data for reprinting."""
    return _last_receipt_data

