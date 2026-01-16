#!/bin/bash
# List all PostgreSQL databases
echo "Attempting to list PostgreSQL databases..."
echo "Method 1: Using postgres user socket"
psql -U postgres -l 2>&1 | head -20

echo ""
echo "Method 2: Using localhost connection"
psql -h localhost -U postgres -l 2>&1 | head -20

echo ""
echo "Method 3: Check if minavigator database exists"
psql -h localhost -U postgres -c "SELECT 1 FROM pg_database WHERE datname='minavigator';" 2>&1
