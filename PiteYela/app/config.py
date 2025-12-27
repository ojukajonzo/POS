"""
Central configuration for Alcohol POS System.
All paths use Windows Documents folder for user data.
"""
import os
from pathlib import Path

# Application metadata
APP_NAME = "Alcohol POS"
APP_VERSION = "1.0.0"

# Get user's Documents folder
DOCUMENTS_FOLDER = Path.home() / "Documents"
BASE_DIR = DOCUMENTS_FOLDER / "PiteYela_PoS"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pos.db"

# Ensure directories exist
BASE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Shop configuration
SHOP_NAME = "PiteYelaHouseofWine_POS"
SHOP_DISPLAY_NAME = "Pite yela House of Wine"
SHOP_LOCATION = "Juba road Opp Jokis Garage, Lira"
SHOP_CONTACT = "0392158188"

# Database settings
DB_TIMEOUT = 20.0

# Receipt settings
RECEIPT_ALCOHOL_WARNING = "18+ Alcohol Warning: This product contains alcohol. Must be 18+ to purchase."

