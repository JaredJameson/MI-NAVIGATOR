import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Get user ID
cursor.execute("SELECT id FROM users WHERE email = 'test@example.com'")
user_row = cursor.fetchone()
if user_row:
    user_id = user_row[0]
    
    # Delete analytics events
    cursor.execute("DELETE FROM analytics_events WHERE user_id = ?", (user_id,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    print(f"User ID: {user_id}")
    print(f"Deleted {deleted_count} analytics events")
    print(f"Usage counter reset to 0/2")
else:
    print("User not found")

conn.close()
