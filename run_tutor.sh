#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Clean up old logs and create a fresh logs directory
rm -rf "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/logs"

# Function to clean up background processes by killing what's on the ports
cleanup() {
    echo "Shutting down tutor..."
    # Use lsof to find and kill processes by port for robust cleanup
    kill $(lsof -t -i:8765) 2>/dev/null
    kill $(lsof -t -i:8000) 2>/dev/null
    kill $(lsof -t -i:3000) 2>/dev/null
    echo "Cleanup complete."
}

# Trap the INT signal (sent by Ctrl+C) to run the cleanup function
trap cleanup INT

# Start the Python backend in the background
echo "Starting Python backend... Logs -> logs/mediamixer.log"
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python MediaMixer/media_mixer.py) > "$SCRIPT_DIR/logs/mediamixer.log" 2>&1 &

# Start the FastAPI server in the background
echo "Starting DASH API server... Logs -> logs/api.log"
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python DashSystem/dash_api.py) > "$SCRIPT_DIR/logs/api.log" 2>&1 &

# Give the backend servers a moment to start
echo "Waiting for backend services to initialize..."
sleep 2

# Start the Node.js frontend in the background
echo "Starting Node.js frontend... Logs -> logs/frontend.log"
(cd "$SCRIPT_DIR/frontend" && npm start) > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &

# Open the browser to the frontend URL
echo "Opening browser..."
open http://localhost:3000

echo "Tutor is running."
echo "Press Ctrl+C to stop."
echo "You can view the logs for each service in the 'logs' directory."

# Wait indefinitely until the script is interrupted
wait