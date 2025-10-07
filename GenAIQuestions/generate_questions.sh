#!/usr/bin/env bash

# File to send
DIR="examples"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Detect Python environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    # Not already in a virtual environment
    if [[ -d "$SCRIPT_DIR/env" ]]; then
        echo "Activating local env..."
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/env/bin/activate"
    elif [[ -d "$SCRIPT_DIR/.env" ]]; then
        echo "Activating local .env..."
        # shellcheck source=/dev/null
        source "$SCRIPT_DIR/.env/bin/activate"
    else
        echo "❌ No virtual environment found."
        echo "👉 Please create one with:"
        echo "    python -m venv env"
        echo "    source env/bin/activate"
        echo "👉 Next, install the required packages with:"
        echo "    pip install -r requirements.txt"
        echo "👉 If you plan to use the frontend, also run:"
        echo "    cd frontend"
        echo "    npm install --force"
        echo "    cd .."
        echo "👉 Finally, run this script again."
        exit 1
    fi
else
    echo "Using already active virtual environment: $VIRTUAL_ENV"
fi

PYTHON_BIN="$(command -v python3 || command -v python)"
echo "Using Python: $PYTHON_BIN"
pids=()

# Function to clean up background processes
cleanup() {
    echo "Shutting down tutor..."
    for pid in "${pids[@]}"; do
        echo "Killing process $pid"
        kill "$pid"
    done
    echo "All processes terminated."
}

trap cleanup INT 

# Start the SherlockEDExam FastAPI server in the background
echo "Starting QUESTION GEN API server... Logs -> logs/api.log"
(cd "$SCRIPT_DIR/server" && "$PYTHON_BIN" run_server.py) > "$SCRIPT_DIR/server/logs/api.logs" 2>&1 &
pids+=($!)

echo "The server is started and runs on the following PIDs: ${pids[*]}"
echo "Press Ctrl+C to stop." 
sleep 5 
echo -e "\nGetting things ready..."
sleep 10


# Endpoint
URL="http://127.0.0.1:8080/questions/generate"

# Check if directory exists
if [ ! -d "$DIR" ]; then
  echo "Error: Directory '$DIR' not found."
  exit 1
fi

# Loop through all JSON files in the directory
for FILE in "$DIR"/*.json; do
  if [ -f "$FILE" ]; then
    echo "Processing: $FILE"
    curl -s -X POST "$URL" \
      -H "Content-Type: application/json" \
      -d @"$FILE"
    echo -e "\n--- Done with $FILE ---\n"
  else
    echo "No JSON files found in $DIR"
    exit 1
  fi
done