#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to clean up background processes
cleanup() {
    echo "Shutting down tutor..."
    # Kill all child processes of this script
    pkill -P $
    echo "All processes terminated."
}

# Trap the INT signal (sent by Ctrl+C) to run the cleanup function
trap cleanup INT

# Start the Python backend in the background
echo "Starting Python backend..."
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python MediaMixer/media_mixer.py) &

# Start the FastAPI server in the background
echo "Starting API server..."
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python api.py) &

# Start the Node.js frontend in the background
echo "Starting Node.js frontend..."
(cd "$SCRIPT_DIR/live-api-web-console" && npm start) &

echo "Tutor is running. Press Ctrl+C to stop."

# Wait indefinitely until the script is interrupted
wait
