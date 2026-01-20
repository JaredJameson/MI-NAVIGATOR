import sqlite3
from datetime import datetime

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Get user
cursor.execute("SELECT id, email, role FROM users WHERE email = 'feature211test@example.com'")
user = cursor.fetchone()

if not user:
    print("User feature211test@example.com not found!")
    exit(1)

user_id = user[0]
print(f"User: {user[1]}")
print(f"Role: {user[2]}")
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
    print("No analytics events this month")

print(f"\nTotal usage: {total}")
print(f"Limit: 2 (for regular users)")
print(f"Remaining: {max(0, 2 - total)}")

if total >= 2:
    print("\n⚠️  USER HAS REACHED THE LIMIT!")
else:
    print(f"\n✓ User can send {2 - total} more message(s)")

conn.close()
