@echo off
echo Building Alcohol POS executable...
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Build the executable using the spec file
echo Building with spec file...
python -m PyInstaller AlcoholPOS.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful! Executable is in the 'dist' folder.
echo.
pause

