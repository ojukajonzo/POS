"""
Add sample items with Uganda-relevant barcodes to the database.
Run this script to populate the database with test products.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_connection
from app.config import BASE_DIR, DATA_DIR

# Sample products with Uganda-relevant barcodes
SAMPLE_PRODUCTS = [
    {
        "id": "6001234567890",  # Standard EAN-13 format
        "name": "Nile Special Beer",
        "description": "Premium Lager Beer 500ml",
        "cost_price": 2500,
        "selling_price": 3500,
        "quantity_stocked": 200
    },
    {
        "id": "6001234567891",
        "name": "Bell Lager Beer",
        "description": "Local Lager Beer 500ml",
        "cost_price": 2000,
        "selling_price": 3000,
        "quantity_stocked": 150
    },
    {
        "id": "6001234567892",
        "name": "Club Pilsner",
        "description": "Pilsner Beer 500ml",
        "cost_price": 2200,
        "selling_price": 3200,
        "quantity_stocked": 180
    },
    {
        "id": "6001234567893",
        "name": "Waragi Premium",
        "description": "Premium Waragi 750ml",
        "cost_price": 15000,
        "selling_price": 20000,
        "quantity_stocked": 50
    },
    {
        "id": "6001234567894",
        "name": "Uganda Waragi",
        "description": "Standard Waragi 750ml",
        "cost_price": 12000,
        "selling_price": 18000,
        "quantity_stocked": 75
    },
    {
        "id": "6001234567895",
        "name": "Red Label Whisky",
        "description": "Johnnie Walker Red Label 750ml",
        "cost_price": 45000,
        "selling_price": 60000,
        "quantity_stocked": 30
    },
    {
        "id": "6001234567896",
        "name": "Smirnoff Vodka",
        "description": "Smirnoff Vodka 750ml",
        "cost_price": 35000,
        "selling_price": 50000,
        "quantity_stocked": 40
    },
    {
        "id": "6001234567897",
        "name": "Hennessy VS",
        "description": "Hennessy VS Cognac 750ml",
        "cost_price": 120000,
        "selling_price": 180000,
        "quantity_stocked": 15
    },
    {
        "id": "6001234567898",
        "name": "Baileys Irish Cream",
        "description": "Baileys Original 750ml",
        "cost_price": 55000,
        "selling_price": 75000,
        "quantity_stocked": 25
    },
    {
        "id": "6001234567899",
        "name": "Amarula Cream",
        "description": "Amarula Cream Liqueur 750ml",
        "cost_price": 50000,
        "selling_price": 70000,
        "quantity_stocked": 20
    },
    {
        "id": "6001234567900",
        "name": "Captain Morgan Rum",
        "description": "Captain Morgan Spiced Rum 750ml",
        "cost_price": 40000,
        "selling_price": 55000,
        "quantity_stocked": 35
    },
    {
        "id": "6001234567901",
        "name": "Gordon's Gin",
        "description": "Gordon's London Dry Gin 750ml",
        "cost_price": 38000,
        "selling_price": 52000,
        "quantity_stocked": 30
    },
    {
        "id": "6001234567902",
        "name": "Jameson Whiskey",
        "description": "Jameson Irish Whiskey 750ml",
        "cost_price": 65000,
        "selling_price": 90000,
        "quantity_stocked": 20
    },
    {
        "id": "6001234567903",
        "name": "Chivas Regal",
        "description": "Chivas Regal 12 Year 750ml",
        "cost_price": 150000,
        "selling_price": 220000,
        "quantity_stocked": 10
    },
    {
        "id": "6001234567904",
        "name": "Jack Daniel's",
        "description": "Jack Daniel's Old No.7 750ml",
        "cost_price": 80000,
        "selling_price": 110000,
        "quantity_stocked": 25
    }
]

def add_sample_items():
    """Add sample items to the database."""
    print("Adding sample items to database...")
    print("=" * 50)
    
    # Ensure database exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        added_count = 0
        skipped_count = 0
        
        for product in SAMPLE_PRODUCTS:
            # Check if product already exists
            cursor.execute("SELECT id FROM products WHERE id = ?", (product["id"],))
            if cursor.fetchone():
                print(f"[SKIP] Product {product['id']} ({product['name']}) already exists")
                skipped_count += 1
                continue
            
            # Calculate profit
            profit = product["selling_price"] - product["cost_price"]
            
            # Insert product
            cursor.execute("""
                INSERT INTO products 
                (id, name, description, cost_price, selling_price, profit, 
                 quantity_stocked, quantity_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product["id"],
                product["name"],
                product["description"],
                product["cost_price"],
                product["selling_price"],
                profit,
                product["quantity_stocked"],
                product["quantity_stocked"]
            ))
            
            print(f"[ADDED] {product['id']} - {product['name']} - UGX {product['selling_price']:,}")
            added_count += 1
        
        conn.commit()
        
        print("=" * 50)
        print(f"Summary:")
        print(f"  Added: {added_count} products")
        print(f"  Skipped: {skipped_count} products (already exist)")
        print(f"  Total: {len(SAMPLE_PRODUCTS)} products")
        print("=" * 50)
        print("\nSample items added successfully!")
        print("\nYou can now test the POS system with these products.")
        print("Use the barcode numbers to scan/enter products.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to add sample items: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(0 if add_sample_items() else 1)

