import sqlite3
from datetime import datetime

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Find user by email
cursor.execute("SELECT id, email, role FROM users WHERE email = 'testusagelimit@test.com'")
user = cursor.fetchone()

if not user:
    print("User not found")
    exit(1)

user_id = user[0]
print(f"User: {user[1]} (Role: {user[2]})")
print(f"User ID: {user_id}")
print()

# Get current month start
now = datetime.utcnow()
start_date = datetime(now.year, now.month, 1)

# Count analytics events
cursor.execute("""
    SELECT event_type, COUNT(*) 
    FROM analytics_events 
    WHERE user_id = ? 
      AND event_type IN ('CHAT_MESSAGE_SENT', 'RESEARCH_STARTED', 'ANALYSIS_COMPLETED')
      AND created_at >= ?
    GROUP BY event_type
""", (user_id, start_date.isoformat()))

events = cursor.fetchall()

total = 0
if events:
    print("Analytics events this month:")
    for event_type, count in events:
        print(f"  {event_type}: {count}")
        total += count
else:
    print("❌ NO analytics events recorded!")

print(f"\nTotal usage: {total}")
print(f"Limit: 2")

if total >= 2:
    print("\n⚠️  USER SHOULD BE BLOCKED (limit reached)")
else:
    print(f"\n✓ User can send {2 - total} more message(s)")

conn.close()
