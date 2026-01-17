#!/bin/bash

# Script to add timezone column if it doesn't exist
DB_PATH="/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/app.db"

# Try to add the column - will fail silently if it already exists
echo "ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'Europe/Warsaw' NOT NULL;" | \
  /usr/bin/env sqlite3 "$DB_PATH" 2>/dev/null || echo "Column may already exist or command failed"

# Verify column was added
echo "Checking if timezone column exists..."
echo "PRAGMA table_info(users);" | /usr/bin/env sqlite3 "$DB_PATH" | grep timezone && \
  echo "✓ Timezone column exists" || echo "✗ Timezone column missing"
