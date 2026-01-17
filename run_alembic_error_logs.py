#!/usr/bin/env python3
import os
import sys

# Change to backend directory
os.chdir('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

# Run alembic upgrade
os.system('./venv/bin/alembic upgrade head')
