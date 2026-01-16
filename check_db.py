#!/usr/bin/env python3
"""Check PostgreSQL database and create if needed"""
import sys

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    # Connect to PostgreSQL server
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='postgres',
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if minavigator database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname='minavigator'")
    exists = cur.fetchone()

    if not exists:
        print("Database 'minavigator' does not exist. Creating...")
        cur.execute("CREATE DATABASE minavigator")
        print("✓ Database created")
    else:
        print("✓ Database 'minavigator' exists")

    # Check if user exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname='minavigator'")
    user_exists = cur.fetchone()

    if not user_exists:
        print("User 'minavigator' does not exist. Creating...")
        cur.execute("CREATE USER minavigator WITH PASSWORD 'minavigator'")
        print("✓ User created")
    else:
        print("✓ User 'minavigator' exists")

    # Grant privileges
    cur.execute("GRANT ALL PRIVILEGES ON DATABASE minavigator TO minavigator")
    print("✓ Privileges granted")

    cur.close()
    conn.close()

    print("\n✓ Database setup complete!")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
