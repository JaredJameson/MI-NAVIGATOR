#!/usr/bin/env python3
"""Run Alembic migration upgrade"""
import sys
sys.path.insert(0, 'backend')

from alembic.config import Config
from alembic import command

alembic_cfg = Config('backend/alembic.ini')
command.upgrade(alembic_cfg, 'head')
print("Migration completed successfully!")
