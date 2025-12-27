# Quick Start Guide - Alcohol POS System

## First Time Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually if you encounter timeout issues:
   ```bash
   pip install PyQt6 bcrypt python-escpos reportlab openpyxl pyinstaller
   ```

2. **Initialize Database**
   ```bash
   python init_database.py
   ```
   
   This will:
   - Create the data directory in `Documents\AlcoholPOS\data`
   - Create the database file `pos.db`
   - Create default admin user (username: `admin`, password: `admin123`)

3. **Run the Application**
   ```bash
   python app/main.py
   ```

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change the default password immediately after first login!

## Building Executable

1. Make sure all dependencies are installed
2. Run the build script:
   ```bash
   build.bat
   ```
3. The executable will be in the `dist` folder

## Creating Installer

1. Install Inno Setup from https://jrsoftware.org/isinfo.php
2. Build the executable first (see above)
3. Open `installer/setup.iss` in Inno Setup Compiler
4. Build the installer
5. The installer will be in `installer_output` folder

## Data Location

All data is stored in:
```
C:\Users\<YourUsername>\Documents\AlcoholPOS\data\pos.db
```

Receipts are saved in:
```
C:\Users\<YourUsername>\Documents\AlcoholPOS\receipts\
```

## Testing

Run the test suite:
```bash
python tests/test_db.py
```

## Troubleshooting

### Database Errors
- Ensure the data directory exists and is writable
- Delete `pos.db` and run `init_database.py` again to reset

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root directory

### Build Errors
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Check that all dependencies are available

## Next Steps

1. Add products to inventory (Admin → Inventory Management)
2. Create cashier accounts (Admin → User Management - if implemented)
3. Start processing sales!

