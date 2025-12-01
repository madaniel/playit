#!/bin/bash
set -e

echo "========================================="
echo "Playit Service with 1Password Integration"
echo "========================================="

# Run the Python script to fetch secrets and capture output
echo "Step 1: Fetching secrets from 1Password..."
SECRET_KEY=$(python3 /app/fetch_secret.py)

# Check if SECRET_KEY was captured successfully
if [ -n "$SECRET_KEY" ]; then
    echo "✓ SECRET_KEY loaded into memory"
else
    echo "✗ Error: Failed to fetch SECRET_KEY"
    exit 1
fi

# Verify SECRET_KEY is set
if [ -z "$SECRET_KEY" ]; then
    echo "✗ Error: SECRET_KEY is not set"
    exit 1
fi

# Export SECRET_KEY so web_server.py can use it
export SECRET_KEY

echo "Step 3: Starting services..."
echo "========================================="

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill -TERM "$PLAYIT_PID" 2>/dev/null
    kill -TERM "$WEB_PID" 2>/dev/null
    wait
    exit 0
}

# Trap signals
trap cleanup SIGTERM SIGINT

# Start Playit Agent in background
echo "Starting Playit Agent..."
playit --secret "$SECRET_KEY" -s &
PLAYIT_PID=$!

# Start Web Server in background
echo "Starting Web Server on port 8080..."
python3 /app/web_server.py &
WEB_PID=$!

# Wait for processes
wait "$PLAYIT_PID" "$WEB_PID"
