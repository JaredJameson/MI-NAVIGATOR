import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check if analytics_events table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%analytic%'")
tables = cursor.fetchall()
print("Analytics tables:", tables)

# If table exists, check its structure and data
if tables:
    cursor.execute("PRAGMA table_info(analytics_events)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  {col}")

    cursor.execute("SELECT COUNT(*) FROM analytics_events")
    count = cursor.fetchone()[0]
    print(f"\nTotal events: {count}")

    if count > 0:
        cursor.execute("SELECT * FROM analytics_events LIMIT 5")
        events = cursor.fetchall()
        print("\nFirst 5 events:")
        for event in events:
            print(f"  {event}")

conn.close()
