#!/usr/bin/env python3
"""Setup PostgreSQL database for MI-Navigator"""
import sys
import subprocess

# Use psql through subprocess to create database
commands = [
    ("Creating database", "CREATE DATABASE minavigator;"),
    ("Creating user", "CREATE USER minavigator WITH PASSWORD 'minavigator';"),
    ("Granting privileges", "GRANT ALL PRIVILEGES ON DATABASE minavigator TO minavigator;"),
]

print("Setting up PostgreSQL database for MI-Navigator...")
print("=" * 60)

for desc, sql in commands:
    print(f"\n{desc}...")
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-c', sql],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 or 'already exists' in result.stderr:
            print(f"✓ {desc} - OK")
        else:
            print(f"⚠ {desc} - {result.stderr.strip()}")
    except Exception as e:
        print(f"✗ {desc} - Error: {e}")

print("\n" + "=" * 60)
print("Database setup complete!")
print("\nConnection details:")
print("  Host: localhost")
print("  Port: 5432")
print("  Database: minavigator")
print("  User: minavigator")
print("  Password: minavigator")
