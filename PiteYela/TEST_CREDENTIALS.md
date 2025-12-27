# Test Credentials for Alcohol POS System

## Default Admin Account

The system automatically creates a default admin account when the database is first initialized.

### Login Credentials:
- **Username**: `admin`
- **Password**: `admin123`

### Account Details:
- **Role**: Admin (full access)
- **Full Name**: Administrator
- **Permissions**: All features enabled

## How to Login

1. Run the application:
   ```bash
   python app/main.py
   ```

2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`

3. Click "Login"

## What You Can Do as Admin

Once logged in as admin, you have access to:

### ✅ Full POS Features
- Process sales
- Scan/enter products
- Complete transactions
- Print receipts

### ✅ Admin Menu (Click "Admin Menu" button)
- **Inventory Management** - Add/Edit/Delete products
- **Sales Reports** - View sales, profit/loss, export to PDF/Excel
- **User Management** - Create/edit cashier accounts
- **Settings** - Configure printer, barcode scanner, shop info
- **Backup & Restore** - Backup and restore database

### ✅ Additional Features
- **Change Password** - Click "Change Password" button in header
- **Reprint Last Receipt** - Available in POS window

## Creating Test Data

### Add Products (Admin Menu → Inventory Management)
1. Click "Add Product"
2. Fill in:
   - Product ID: `TEST001`
   - Product Name: `Test Beer`
   - Cost Price: `10.00`
   - Selling Price: `15.00`
   - Quantity to Stock: `100`
3. Click "Save"

### Create a Cashier Account (Admin Menu → User Management)
1. Click "Add User"
2. Fill in:
   - Username: `cashier1`
   - Full Name: `Test Cashier`
   - Role: `cashier`
   - Password: `cashier123`
3. Click "Save"

### Test a Sale
1. In POS window, enter product ID: `TEST001`
2. Press Enter
3. Click "Next Item" to add to cart
4. Click "Complete Sale"
5. Receipt will be printed/saved

## Security Note

⚠️ **IMPORTANT**: Change the default admin password immediately after first login!

1. Click "Change Password" button
2. Enter:
   - Current Password: `admin123`
   - New Password: (your secure password)
   - Confirm Password: (same password)
3. Click "Change Password"

## Troubleshooting

### If login fails:
1. Make sure database is initialized:
   ```bash
   python init_database.py
   ```

2. Verify database exists:
   - Location: `C:\Users\<YourUsername>\Documents\AlcoholPOS\data\pos.db`

3. Check if admin user exists:
   ```bash
   python -c "import sys; sys.path.insert(0, 'app'); from app.auth import login; success, user, msg = login('admin', 'admin123'); print('Login:', 'SUCCESS' if success else 'FAILED', '-', msg)"
   ```

## Test Checklist

- [ ] Login with admin/admin123
- [ ] Add a test product
- [ ] Process a test sale
- [ ] View sales report
- [ ] Export report to PDF
- [ ] Export report to Excel
- [ ] Create a cashier account
- [ ] Change admin password
- [ ] Create a backup

---

**Ready to test!** Use `admin` / `admin123` to get started.

