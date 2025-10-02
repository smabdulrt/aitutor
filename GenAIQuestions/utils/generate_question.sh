#!/usr/bin/env bash

# File to send
FILE="example.json"

# Endpoint
URL="http://127.0.0.1:8001/api/questions/generate"

# Check if file exists
if [ ! -f "$FILE" ]; then
  echo "Error: $FILE not found in current directory."
  exit 1
fi

# Make the POST request
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d @"$FILE"
