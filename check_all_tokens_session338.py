import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM password_reset_tokens")
count = cursor.fetchone()[0]
print(f"Total reset tokens in database: {count}")

if count > 0:
    cursor.execute("""
        SELECT prt.token, u.email, prt.created_at, prt.expires_at, prt.used
        FROM password_reset_tokens prt
        JOIN users u ON prt.user_id = u.id
        ORDER BY prt.created_at DESC
        LIMIT 5
    """)
    tokens = cursor.fetchall()
    print("\nLatest reset tokens:")
    for token in tokens:
        print(f"  Email: {token[1]} | Created: {token[2]} | Used: {token[4]}")

conn.close()
