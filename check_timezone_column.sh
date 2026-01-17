#!/bin/bash
sqlite3 /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/app.db "PRAGMA table_info(users);" | grep timezone
