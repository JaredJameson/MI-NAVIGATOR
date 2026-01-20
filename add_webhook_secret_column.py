"""Add secret column to webhooks table."""
import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(webhooks)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'secret' not in columns:
        print("Adding 'secret' column to webhooks table...")
        cursor.execute("ALTER TABLE webhooks ADD COLUMN secret TEXT")
        conn.commit()
        print("✅ Column 'secret' added successfully!")
    else:
        print("✅ Column 'secret' already exists!")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
