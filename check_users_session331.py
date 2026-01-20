#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

print("=== Użytkownicy w bazie danych ===")
cursor.execute('SELECT id, email, role FROM users LIMIT 10')
users = cursor.fetchall()

if not users:
    print("BRAK UŻYTKOWNIKÓW W BAZIE!")
else:
    for user in users:
        print(f"ID: {user[0][:36]} | Email: {user[1]:30s} | Role: {user[2]}")

print(f"\nCałkowita liczba użytkowników: {len(users)}")

# Sprawdź czy istnieje użytkownik z problematycznym ID
problematic_id = "b40eb11f-7118-4e66-b2cd-a5c130283 9cc"
cursor.execute('SELECT id, email FROM users WHERE id LIKE ?', (problematic_id[:20] + '%',))
found = cursor.fetchone()

print(f"\nCzy istnieje użytkownik b40eb11f...? {'TAK' if found else 'NIE'}")

conn.close()
