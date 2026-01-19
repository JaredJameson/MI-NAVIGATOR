#!/bin/sh
backend/venv/bin/python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
# Fix: Use uppercase ADMIN to match enum
cursor.execute("UPDATE users SET role = 'ADMIN' WHERE email = 'admin254@test.com'")
conn.commit()
cursor.execute("SELECT email, role FROM users WHERE email = 'admin254@test.com'")
user = cursor.fetchone()
if user:
    print(f"✓ Fixed {user[0]} to role: {user[1]}")
else:
    print("✗ User not found")
conn.close()
EOF
