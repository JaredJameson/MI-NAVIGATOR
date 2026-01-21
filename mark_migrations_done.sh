#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
# Mark all migrations as executed without running them
./venv/bin/alembic stamp head
