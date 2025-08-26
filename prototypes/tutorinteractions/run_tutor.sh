#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start the Python backend in the background
echo "Starting Python backend..."
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python MediaMixer/media_mixer.py) &

# Start the FastAPI server in the background
echo "Starting API server..."
(cd "$SCRIPT_DIR" && /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python api.py) &

# Start the Node.js frontend in the background
echo "Starting Node.js frontend..."
(cd "$SCRIPT_DIR/live-api-web-console" && npm start) &

echo "Tutor is running. To stop the processes, you may need to manually find and kill them."
