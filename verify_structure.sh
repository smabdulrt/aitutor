#!/bin/bash

echo "🔍 Verifying project structure..."

# Check DashSystem
echo ""
echo "Checking DashSystem..."
if [ -f "DashSystem/Dockerfile" ]; then
    echo "✅ DashSystem/Dockerfile found"
else
    echo "❌ DashSystem/Dockerfile NOT found"
fi

if [ -f "DashSystem/requirements.txt" ]; then
    echo "✅ DashSystem/requirements.txt found"
else
    echo "❌ DashSystem/requirements.txt NOT found"
fi

if [ -f "DashSystem/dash_api.py" ]; then
    echo "✅ DashSystem/dash_api.py found"
else
    echo "❌ DashSystem/dash_api.py NOT found"
fi

# Check SherlockEDApi
echo ""
echo "Checking SherlockEDApi..."
if [ -f "SherlockEDApi/Dockerfile" ]; then
    echo "✅ SherlockEDApi/Dockerfile found"
else
    echo "❌ SherlockEDApi/Dockerfile NOT found"
fi

if [ -f "SherlockEDApi/requirements.txt" ]; then
    echo "✅ SherlockEDApi/requirements.txt found"
else
    echo "❌ SherlockEDApi/requirements.txt NOT found"
fi

if [ -f "SherlockEDApi/run_backend.py" ]; then
    echo "✅ SherlockEDApi/run_backend.py found"
else
    echo "❌ SherlockEDApi/run_backend.py NOT found"
fi

# Check MediaMixer
echo ""
echo "Checking MediaMixer..."
if [ -f "MediaMixer/Dockerfile" ]; then
    echo "✅ MediaMixer/Dockerfile found"
else
    echo "❌ MediaMixer/Dockerfile NOT found"
fi

if [ -f "MediaMixer/requirements.txt" ]; then
    echo "✅ MediaMixer/requirements.txt found"
else
    echo "❌ MediaMixer/requirements.txt NOT found"
fi

if [ -f "MediaMixer/media_mixer.py" ]; then
    echo "✅ MediaMixer/media_mixer.py found"
else
    echo "❌ MediaMixer/media_mixer.py NOT found"
fi

# Check Frontend
echo ""
echo "Checking Frontend..."
if [ -f "frontend/Dockerfile" ]; then
    echo "✅ frontend/Dockerfile found"
else
    echo "❌ frontend/Dockerfile NOT found"
fi

if [ -f "frontend/package.json" ]; then
    echo "✅ frontend/package.json found"
else
    echo "❌ frontend/package.json NOT found"
fi

echo ""
echo "✅ Verification complete!"
