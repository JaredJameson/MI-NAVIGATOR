#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
