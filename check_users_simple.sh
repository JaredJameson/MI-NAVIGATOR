#!/bin/bash
echo "SELECT email FROM users;" | backend/venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute('SELECT email, name FROM users LIMIT 10')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]}')
conn.close()
"
