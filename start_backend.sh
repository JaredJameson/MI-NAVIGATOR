#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
