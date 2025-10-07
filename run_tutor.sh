#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Clean up old logs and create a fresh logs directory
rm -rf "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/logs"

# Use the specific Python from the aitutor venv
PYTHON_BIN="/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python"

if [[ ! -f "$PYTHON_BIN" ]]; then
    echo "❌ Python not found at: $PYTHON_BIN"
    echo "👉 Please check your virtual environment setup."
    exit 1
fi

echo "Using Python: $PYTHON_BIN"

# Array to hold the PIDs of background processes
pids=()

# Function to clean up background processes
cleanup() {
    echo "Shutting down tutor..."
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Sending SIGTERM to process $pid"
            kill -TERM "$pid" 2>/dev/null
        fi
    done

    # Wait briefly for graceful shutdown
    sleep 2

    # Force kill any remaining processes
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Force killing process $pid"
            kill -9 "$pid" 2>/dev/null
        fi
    done

    # Kill any lingering processes on MediaMixer ports
    lsof -ti:8765 | xargs -r kill -9 2>/dev/null || true
    lsof -ti:8766 | xargs -r kill -9 2>/dev/null || true

    echo "All processes terminated."
}

# Trap the INT signal (sent by Ctrl+C) to run the cleanup function
trap cleanup INT
trap cleanup EXIT

# Start the Python backend in the background
echo "Starting Python backend... Logs -> logs/mediamixer.log"
(cd "$SCRIPT_DIR" && "$PYTHON_BIN" MediaMixer/media_mixer.py) > "$SCRIPT_DIR/logs/mediamixer.log" 2>&1 &
pids+=($!)

# Start the FastAPI server in the background
echo "Starting DASH API server... Logs -> logs/dashsystem.log"
(cd "$SCRIPT_DIR" && "$PYTHON_BIN" DashSystem/dash_api.py) > "$SCRIPT_DIR/logs/dashsystem.log" 2>&1 &
pids+=($!)

# Start the SherlockEDExam FastAPI server in the background
echo "Starting SherlockED Exam API server... Logs -> logs/api.log"
(cd "$SCRIPT_DIR" && "$PYTHON_BIN" SherlockEDApi/run_backend.py) > "$SCRIPT_DIR/logs/sherlocked_exam.log" 2>&1 &
pids+=($!)

# Give the backend servers a moment to start
echo "Waiting for backend services to initialize..."
sleep 2

# Extract ports dynamically from configuration files
FRONTEND_PORT=$(grep -o '"port":[[:space:]]*[0-9]*' "$SCRIPT_DIR/frontend/vite.config.ts" 2>/dev/null | grep -o '[0-9]*' || echo "3000")
DASH_API_PORT=$(grep -o 'port=[0-9]*' "$SCRIPT_DIR/DashSystem/dash_api.py" 2>/dev/null | grep -o '[0-9]*' || echo "8000")
SHERLOCKED_API_PORT=$(grep -o 'port=[0-9]*' "$SCRIPT_DIR/SherlockEDApi/run_backend.py" 2>/dev/null | grep -o '[0-9]*' || echo "8001")
MEDIAMIXER_COMMAND_PORT=$(grep -o 'localhost",[[:space:]]*[0-9]*' "$SCRIPT_DIR/MediaMixer/media_mixer.py" 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "8765")
MEDIAMIXER_VIDEO_PORT=$(grep -o 'localhost",[[:space:]]*[0-9]*' "$SCRIPT_DIR/MediaMixer/media_mixer.py" 2>/dev/null | tail -1 | grep -o '[0-9]*' || echo "8766")

# Start the Node.js frontend in the background
echo "Starting Node.js frontend... Logs -> logs/frontend.log"
(cd "$SCRIPT_DIR/frontend" && npm run dev) > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
pids+=($!)

echo "Tutor is running with the following PIDs: ${pids[*]}"
echo ""
echo "📡 Service URLs:"
echo "  🌐 Frontend:           http://localhost:$FRONTEND_PORT"
echo "  🔧 DASH API:           http://localhost:$DASH_API_PORT"
echo "  🕵️  SherlockED API:     http://localhost:$SHERLOCKED_API_PORT"
echo "  📹 MediaMixer Command: ws://localhost:$MEDIAMIXER_COMMAND_PORT"
echo "  📺 MediaMixer Video:   ws://localhost:$MEDIAMIXER_VIDEO_PORT"
echo ""
echo "Press Ctrl+C to stop."
echo "You can view the logs for each service in the 'logs' directory."

# Wait indefinitely until the script is interrupted
wait
