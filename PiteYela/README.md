# Alcohol POS System

A production-grade Point of Sale (POS) system for alcohol retail, built with Python and PyQt6.

## Features

- **Role-Based Access Control**: Admin and Cashier roles with different permissions
- **Product Inventory Management**: Full CRUD operations for products with auto-calculated profit
- **Point of Sale Interface**: Fast, keyboard-friendly POS with barcode scanner support
- **Sales Reporting**: Comprehensive sales reports with date filtering and profit/loss analysis
- **Receipt Printing**: ESC/POS printer support with receipt formatting
- **Offline Operation**: SQLite database for local, offline operation
- **Windows Installer**: Easy installation via .exe installer

## Installation

### Prerequisites

- Windows 10 or later
- Python 3.8+ (for development)

### Building from Source

1. Clone the repository:
```bash
git clone <repository-url>
cd PiteYela
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/main.py
```

### Building Executable

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the build script:
```bash
build.bat
```

3. The executable will be in the `dist` folder.

### Creating Installer

1. Install Inno Setup from https://jrsoftware.org/isinfo.php

2. Build the executable first (see above)

3. Open `installer/setup.iss` in Inno Setup Compiler

4. Build the installer

## Default Login

- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change the default password after first login!

## Project Structure

```
pos/
├── app/
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration and paths
│   ├── database.py      # Database connection and schema
│   ├── models.py        # Business logic and data models
│   ├── auth.py          # Authentication
│   ├── pos.py           # Main POS interface
│   ├── inventory.py     # Inventory management (Admin)
│   ├── reports.py       # Sales reports (Admin)
│   ├── printer.py       # Receipt printing
│   └── utils.py         # Utility functions
├── assets/
│   ├── logo.png
│   └── styles.qss
├── installer/
│   └── setup.iss        # Inno Setup installer script
├── data/                # Database storage (created automatically)
├── tests/
│   └── test_db.py
├── requirements.txt
├── build.bat
└── README.md
```

## Data Storage

The application stores all data in:
```
C:\Users\<YourUsername>\Documents\AlcoholPOS\data\pos.db
```

This includes:
- User accounts
- Product inventory
- Sales transactions
- Receipt files (in `receipts/` subfolder)

## User Roles

### Admin
- Full access to all features
- Can perform sales (like cashier)
- View all cashiers' sales
- Manage inventory (add/edit/delete products)
- Generate sales reports
- View profit/loss analysis
- Manage users (add/edit cashiers)
- Reprint receipts

### Cashier
- Login and perform sales only
- Scan or manually enter product codes
- Print receipts
- Cannot:
  - Edit prices or products
  - View other cashiers' sales
  - Access reports or profit/loss data

## Usage

### Starting a Sale

1. Enter or scan product ID in the Product ID field
2. Press Enter or click "Next Item"
3. Adjust quantity if needed
4. Click "Next Item" to add to cart
5. Repeat for all items
6. Click "Complete Sale" when done
7. Receipt will be printed automatically

### Managing Inventory (Admin)

1. Click "Admin Menu" → "Inventory Management"
2. Click "Add Product" to add new products
3. Select a product and click "Edit Product" to modify
4. Select a product and click "Delete Product" to remove

### Viewing Reports (Admin)

1. Click "Admin Menu" → "Sales Reports"
2. Select date period (Day/Week/Month/Custom Range)
3. Click "Generate Report"
4. View sales summary, transactions, and profit/loss

## Keyboard Shortcuts

- **Enter**: Process product ID entry
- **Escape**: Cancel current sale
- **F1**: Open admin menu (Admin only)

## Development

### Running Tests

```bash
python tests/test_db.py
```

### Database Schema

The system uses SQLite with the following tables:
- `users`: User accounts and roles
- `products`: Product inventory
- `sales`: Sales transactions
- `sale_items`: Individual items in each sale

## Troubleshooting

### Database Errors

If you encounter database errors:
1. Check that the data directory exists: `Documents\AlcoholPOS\data`
2. Ensure you have write permissions
3. Delete `pos.db` to reset (will lose all data)

### Printer Issues

If receipt printing fails:
- Receipts are saved as text files in `Documents\AlcoholPOS\receipts\`
- Check printer connection and drivers
- Ensure ESC/POS compatible printer is configured

## License

This is a commercial POS system. All rights reserved.

## Support

For issues or questions, contact your system administrator.
