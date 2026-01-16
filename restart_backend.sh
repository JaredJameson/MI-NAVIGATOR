#!/bin/bash
# Restart backend with SQLite support

cd "$(dirname "$0")"

echo "Installing aiosqlite..."
backend/venv/bin/pip install -q aiosqlite

echo "Stopping old backend process..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2

echo "Starting backend..."
cd backend
./venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✓ Backend is running"
    curl -s http://localhost:8000/health && echo " - Health check passed"
else
    echo "✗ Backend failed to start"
    tail -20 ../backend.log
    exit 1
fi
