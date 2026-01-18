#!/bin/bash
exec /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
