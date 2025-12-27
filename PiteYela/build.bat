@echo off
echo Building Alcohol POS executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Build the executable
REM Note: If logo.ico doesn't exist, remove --icon parameter
if exist assets\logo.ico (
    python -m PyInstaller --onefile --windowed --name "AlcoholPOS" --icon=assets/logo.ico app/main.py
) else (
    python -m PyInstaller --onefile --windowed --name "AlcoholPOS" app/main.py
)

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful! Executable is in the 'dist' folder.
echo.
pause

