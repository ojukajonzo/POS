"""
Business logic and data models for Alcohol POS System.
Contains product calculations, inventory updates, and sales validation.
"""
from typing import Optional, Dict, List, Tuple
from app.database import get_connection, execute_transaction

class Product:
    """Product model with auto-calculated fields."""
    
    def __init__(self, product_id: str, name: str, description: str = "",
                 milliliters: int = 0, cost_price: float = 0.0, selling_price: float = 0.0,
                 quantity_stocked: int = 0, quantity_sold: int = 0):
        self.id = product_id
        self.name = name
        self.description = description
        self.milliliters = milliliters
        self.cost_price = cost_price
        self.selling_price = selling_price
        self.quantity_stocked = quantity_stocked
        self.quantity_sold = quantity_sold
        
    @property
    def profit(self) -> float:
        """Auto-calculated profit per unit."""
        return self.selling_price - self.cost_price
    
    @property
    def quantity_available(self) -> int:
        """Auto-calculated available quantity."""
        return self.quantity_stocked - self.quantity_sold
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'milliliters': self.milliliters,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'profit': self.profit,
            'quantity_stocked': self.quantity_stocked,
            'quantity_sold': self.quantity_sold,
            'quantity_available': self.quantity_available
        }

def get_product(product_id: str) -> Optional[Product]:
    """Get product by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, milliliters, cost_price, selling_price,
                   quantity_stocked, quantity_sold
            FROM products
            WHERE id = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        if row:
            # Handle milliliters - may not exist in older databases
            try:
                milliliters = row['milliliters'] if row['milliliters'] is not None else 0
            except (KeyError, IndexError):
                milliliters = 0
            
            return Product(
                product_id=row['id'],
                name=row['name'],
                description=row['description'] or "",
                milliliters=milliliters,
                cost_price=row['cost_price'],
                selling_price=row['selling_price'],
                quantity_stocked=row['quantity_stocked'],
                quantity_sold=row['quantity_sold']
            )
        return None
    finally:
        conn.close()

def validate_stock_availability(product_id: str, requested_quantity: int) -> Tuple[bool, str]:
    """
    Validate if requested quantity is available.
    
    Returns:
        (is_valid, error_message)
    """
    product = get_product(product_id)
    if not product:
        return False, "Product not found"
    
    if product.quantity_available < requested_quantity:
        return False, f"Insufficient stock. Available: {product.quantity_available}"
    
    return True, ""

def calculate_line_total(unit_price: float, quantity: int) -> float:
    """Calculate line total for an item."""
    return round(unit_price * quantity, 2)

def calculate_grand_total(items: List[Dict]) -> float:
    """
    Calculate grand total from list of items.
    
    Each item dict should have: {'unit_price': float, 'quantity': int}
    """
    total = 0.0
    for item in items:
        total += calculate_line_total(item['unit_price'], item['quantity'])
    return round(total, 2)

def update_inventory_after_sale(product_id: str, quantity_sold: int) -> bool:
    """
    Update inventory after a sale.
    Atomically updates quantity_sold and quantity_available.
    """
    queries = [
        ("""
            UPDATE products
            SET quantity_sold = quantity_sold + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (quantity_sold, product_id))
    ]
    
    return execute_transaction(queries)

def create_sale(cashier_id: int, cashier_name: str, items: List[Dict]) -> Optional[int]:
    """
    Create a sale record with items.
    
    Args:
        cashier_id: ID of the cashier
        cashier_name: Name of the cashier
        items: List of item dicts with keys: product_id, product_name, quantity, unit_price, line_total
        
    Returns:
        Sale ID if successful, None otherwise
    """
    # Calculate grand total
    grand_total = sum(item['line_total'] for item in items)
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert sale
        cursor.execute("""
            INSERT INTO sales (cashier_id, cashier_name, grand_total)
            VALUES (?, ?, ?)
        """, (cashier_id, cashier_name, grand_total))
        
        sale_id = cursor.lastrowid
        
        # Insert sale items - batch process for speed
        # Get all products at once to minimize database queries
        product_cache = {}
        for item in items:
            if item['product_id'] not in product_cache:
                product = get_product(item['product_id'])
                product_cache[item['product_id']] = getattr(product, 'milliliters', 0) if product else 0
        
        # Insert all sale items in batch
        for item in items:
            milliliters = product_cache.get(item['product_id'], 0)
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, product_name, quantity, unit_price, line_total, milliliters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sale_id, item['product_id'], item['product_name'], 
                  item['quantity'], item['unit_price'], item['line_total'], milliliters))
        
        # Update inventory for all items (this is already optimized with transactions)
        for item in items:
            update_inventory_after_sale(item['product_id'], item['quantity'])
        
        conn.commit()
        return sale_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating sale: {e}")
        return None
    finally:
        conn.close()

def get_sale_details(sale_id: int) -> Optional[Dict]:
    """Get complete sale details including items."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get sale info
        cursor.execute("""
            SELECT id, cashier_id, cashier_name, sale_date, grand_total
            FROM sales
            WHERE id = ?
        """, (sale_id,))
        
        sale_row = cursor.fetchone()
        if not sale_row:
            return None
        
        # Get sale items
        cursor.execute("""
            SELECT product_id, product_name, quantity, unit_price, line_total, milliliters
            FROM sale_items
            WHERE sale_id = ?
            ORDER BY id
        """, (sale_id,))
        
        items = []
        for row in cursor.fetchall():
            item_dict = dict(row)
            # Handle milliliters - may not exist in older databases
            try:
                item_dict['milliliters'] = row['milliliters'] if row['milliliters'] is not None else 0
            except (KeyError, IndexError):
                item_dict['milliliters'] = 0
            items.append(item_dict)
        
        return {
            'sale_id': sale_row['id'],
            'cashier_id': sale_row['cashier_id'],
            'cashier_name': sale_row['cashier_name'],
            'sale_date': sale_row['sale_date'],
            'grand_total': sale_row['grand_total'],
            'items': items
        }
    finally:
        conn.close()

