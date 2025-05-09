#!/bin/bash

# Function to handle cleanup on script exit
cleanup() {
    echo "Shutting down services..."
    # Kill all background processes
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handling
trap cleanup SIGTERM SIGINT

# Start the FastAPI server
echo "Starting FastAPI server..."
uvicorn asgi_server:app --host 0.0.0.0 --port 8000 --workers 10 &
FASTAPI_PID=$!

# Start any other services here
# For example, if you have a worker process:
# echo "Starting worker process..."
# python worker.py &
# WORKER_PID=$!

# Wait for all background processes
wait

# If we get here, something went wrong
echo "One or more processes exited unexpectedly"
exit 1
