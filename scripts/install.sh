#!/bin/bash

echo "Installing Edge Favorites to PDF Converter..."
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ first"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package
echo "Installing package..."
pip install -e .

echo
echo "Installation complete!"
echo
echo "To use the converter:"
echo "  1. Run: source venv/bin/activate"
echo "  2. Run: edge2pdf --help"
echo

# Make script executable
chmod +x scripts/install.sh