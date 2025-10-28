#!/bin/bash
# Space Haven Save Editor Launcher
# This script launches the Python version of the Space Haven Save Editor using uv

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    echo "This will download and install uv (the fast Python package manager)"
    
    # Install uv using the standalone installer
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Check if installation was successful
    if ! command -v uv &> /dev/null; then
        echo "Error: Failed to install uv."
        echo "Please install manually: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    echo "✓ uv installed successfully!"
fi

# Launch the editor using uv run
# uv will automatically create a virtual environment and install dependencies
echo "Starting Space Haven Save Editor..."
echo "(uv will handle dependencies automatically)"

uv run --with PyQt6 space_haven_editor.py

# Exit with the same exit code as the Python script
exit $?
