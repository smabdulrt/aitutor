#!/bin/bash

# Diagnostic script for Teaching Assistant integration
# This script checks if all services are running and accessible

echo "=== Teaching Assistant Integration Diagnostics ==="
echo ""

# Check if MediaMixer is running on port 8765
echo "1. Checking MediaMixer WebSocket (port 8765)..."
if nc -z localhost 8765 2>/dev/null; then
    echo "   ✓ MediaMixer is running on port 8765"
else
    echo "   ✗ MediaMixer is NOT running on port 8765"
    echo "   → Start it with: python3 MediaMixer/media_mixer.py"
fi
echo ""

# Check if TA Server is running on port 8766
echo "2. Checking TA Server WebSocket (port 8766)..."
if nc -z localhost 8766 2>/dev/null; then
    echo "   ✓ TA Server is running on port 8766"
else
    echo "   ✗ TA Server is NOT running on port 8766"
    echo "   → Start it with: python3 -m backend.teaching_assistant.ta_server"
fi
echo ""

# Check if Frontend is running on port 3000
echo "3. Checking Frontend (port 3000)..."
if nc -z localhost 3000 2>/dev/null; then
    echo "   ✓ Frontend is running on port 3000"
else
    echo "   ✗ Frontend is NOT running on port 3000"
    echo "   → Start it with: cd frontend && npm start"
fi
echo ""

# Check log files if they exist
echo "4. Checking log files..."
if [ -f "logs/ta_server.log" ]; then
    echo "   TA Server log (last 5 lines):"
    tail -5 logs/ta_server.log | sed 's/^/     /'
else
    echo "   ⚠ No TA Server log file found"
fi
echo ""

if [ -f "logs/mediamixer.log" ]; then
    echo "   MediaMixer log (last 5 lines):"
    tail -5 logs/mediamixer.log | sed 's/^/     /'
else
    echo "   ⚠ No MediaMixer log file found"
fi
echo ""

if [ -f "logs/frontend.log" ]; then
    echo "   Frontend log (last 5 lines):"
    tail -5 logs/frontend.log | sed 's/^/     /'
else
    echo "   ⚠ No Frontend log file found"
fi
echo ""

# Check Python dependencies
echo "5. Checking Python dependencies..."
python3 -c "import websockets; print('   ✓ websockets module installed')" 2>/dev/null || echo "   ✗ websockets module NOT installed (pip install websockets)"
python3 -c "import asyncio; print('   ✓ asyncio module available')" 2>/dev/null || echo "   ✗ asyncio module NOT available"
echo ""

# Check if run_tutor.sh processes are running
echo "6. Checking running processes..."
if pgrep -f "backend.teaching_assistant.ta_server" > /dev/null; then
    echo "   ✓ TA Server process is running"
else
    echo "   ✗ TA Server process is NOT running"
fi

if pgrep -f "MediaMixer/media_mixer.py" > /dev/null; then
    echo "   ✓ MediaMixer process is running"
else
    echo "   ✗ MediaMixer process is NOT running"
fi

if pgrep -f "react-scripts start" > /dev/null; then
    echo "   ✓ Frontend (React) process is running"
else
    echo "   ✗ Frontend process is NOT running"
fi
echo ""

echo "=== Diagnostics Complete ==="
echo ""
echo "If all services are running but tests still fail, check:"
echo "  1. Browser console errors (F12 in Chrome/Firefox)"
echo "  2. Backend logs in the logs/ directory"
echo "  3. WebSocket connection errors in frontend console"
