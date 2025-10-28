#!/bin/bash
# Space Haven Save Editor Launcher
# This script launches the Python version of the Space Haven Save Editor

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check if PyQt6 is installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "PyQt6 is not installed. Installing dependencies..."
    pip install --user -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        echo "Please run: pip install --user PyQt6"
        exit 1
    fi
fi

# Launch the editor
echo "Starting Space Haven Save Editor..."
python3 space_haven_editor.py

# Exit with the same exit code as the Python script
exit $?
