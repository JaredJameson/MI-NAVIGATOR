import sqlite3
import json

conn = sqlite3.connect('features.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, description, steps, passes FROM features WHERE id = 76')
row = cursor.fetchone()
if row:
    print(f'ID: {row[0]}')
    print(f'Name: {row[1]}')
    print(f'Description: {row[2]}')
    print(f'Steps: {row[3]}')
    print(f'Passes: {row[4]}')
conn.close()
