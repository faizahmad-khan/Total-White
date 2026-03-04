@echo off
REM Camouflage: Web Build Script (Windows)
REM This script rebuilds the game for web deployment via Pygbag

echo ======================================
echo Camouflage: Web Build Helper
echo ======================================
echo.

REM Check if pygbag is installed
python -c "import pygbag" 2>nul
if errorlevel 1 (
    echo [*] pygbag not found. Installing...
    pip install --upgrade pygbag
    if errorlevel 1 (
        echo [-] Failed to install pygbag
        exit /b 1
    )
)

echo [+] pygbag is installed
echo.
echo [*] Building web version...
echo.

REM Run pygbag build
python -m pygbag main.py --build

if errorlevel 1 (
    echo.
    echo [-] Build failed. See errors above.
    exit /b 1
)

echo.
echo [+] Build successful!
echo.
echo Web build location: build\web\
echo Upload this folder: build\web\
echo.
echo Next steps:
echo 1. Go to https://itch.io/dashboard
echo 2. Create a new project called 'Camouflage: Advanced Stealth Game'
echo 3. Upload the 'web' folder as an HTML5 game
echo 4. Set game canvas to 800x600
echo.
echo For detailed instructions, see DEPLOYMENT.md
