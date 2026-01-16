#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
./venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
