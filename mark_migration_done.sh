#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
export PYTHONPATH=/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend

# Mark the migration as done without actually running it
./venv/bin/alembic stamp 4a5b6c7d8e9f
