#!/bin/bash

# Determine the directory where this script is located
PROJECT_DIR=$(dirname "$(realpath "$0")")

SERVICE_FILE="$PROJECT_DIR/valve-server.service"
RUN_SCRIPT="$PROJECT_DIR/run.sh"

OS=$(uname)

if [ "$OS" = "Darwin" ]; then
    # Replace the hardcoded paths in the .service and run.sh files
    sed -i '' "s|path_to_project|$PROJECT_DIR|g" "$SERVICE_FILE"
    sed -i '' "s|path_to_project|$PROJECT_DIR|g" "$RUN_SCRIPT"
else
    # Linux - slightly different syntax
    sed -i "s|path_to_project|$PROJECT_DIR|g" "$SERVICE_FILE"
    sed -i "s|path_to_project|$PROJECT_DIR|g" "$RUN_SCRIPT"    
fi

echo "Paths in valve-server.service and run.sh have been updated to $PROJECT_DIR"


# Change to the project directory
cd "$PROJECT_DIR" || { echo "Failed to cd to $PROJECT_DIR"; exit 1; }

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required Python packages
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found, skipping pip install."
fi

echo "Python virtual environment created and dependencies installed."
echo "Done with setup."
