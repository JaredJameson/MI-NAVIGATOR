#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 > ../backend_session329_restart.log 2>&1 &
echo "Backend restarted on port 8000"
