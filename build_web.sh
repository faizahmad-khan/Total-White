#!/bin/bash

# Camouflage: Web Build Script
# This script rebuilds the game for web deployment via Pygbag

echo "======================================"
echo "Camouflage: Web Build Helper"
echo "======================================"
echo ""

# Check if pygbag is installed
if ! python3 -c "import pygbag" 2>/dev/null; then
    echo "❌ pygbag not found. Installing..."
    pip install --upgrade pygbag
    if [ $? -ne 0 ]; then
        echo "Failed to install pygbag"
        exit 1
    fi
fi

echo "✅ pygbag is installed"
echo ""
echo "🔨 Building web version..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Run pygbag build
python3 -m pygbag main.py --build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📁 Web build location: ./build/web/"
    echo "📄 Upload this: ./build/web/"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://itch.io/dashboard"
    echo "2. Create a new project called 'Camouflage: Advanced Stealth Game'"
    echo "3. Upload the 'web' folder as an HTML5 game"
    echo "4. Set game canvas to 800x600"
    echo ""
    echo "For detailed instructions, see DEPLOYMENT.md"
else
    echo ""
    echo "❌ Build failed. See errors above."
    exit 1
fi
