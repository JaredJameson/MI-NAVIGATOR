#!/bin/sh
backend/venv/bin/uvicorn test_webhook_server:app --host 0.0.0.0 --port 8001 > test_webhook_server.log 2>&1 &
echo $! > test_webhook_server.pid
echo "Test webhook server started on port 8001 (PID: $(cat test_webhook_server.pid))"
