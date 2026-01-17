#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
export PYTHONPATH=/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
./venv/bin/alembic downgrade -1
