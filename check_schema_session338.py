import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check if password_reset_tokens table exists
if ('password_reset_tokens',) in tables:
    cursor.execute("PRAGMA table_info(password_reset_tokens);")
    columns = cursor.fetchall()
    print("\npassword_reset_tokens columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\n⚠️ password_reset_tokens table does NOT exist!")

conn.close()
