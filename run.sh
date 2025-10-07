#!/bin/bash
# Damancom Login Automation Runner (Linux/Mac)

echo "======================================="
echo "  Damancom Login Automation"
echo "======================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

# Auto-install requirements
echo "Checking and installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "⚠️  Warning: Some dependencies may not have installed correctly"
fi
echo ""

# Show menu
echo "Choose which script to run:"
echo "1) Command-line version"
echo "2) GUI version"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Starting command-line version..."
        echo ""
        python3 main.py
        ;;
    2)
        echo ""
        echo "Starting GUI version..."
        echo ""
        python3 gui_login.py
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
