import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT email, default_analysis_depth FROM users WHERE email LIKE '%regression%' LIMIT 1")
result = cursor.fetchone()
print(f"Email: {result[0]}, default_analysis_depth: {result[1]}")
conn.close()
