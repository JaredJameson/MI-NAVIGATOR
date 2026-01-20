import sqlite3
from datetime import datetime

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Get user info
cursor.execute("SELECT id, email, role FROM users WHERE email = ?", ('test_session318@test.com',))
user_row = cursor.fetchone()

if user_row:
    user_id, email, role = user_row
    print(f"User: {email}")
    print(f"Role: {role}")
    print(f"User ID: {user_id}")

    # Count current month's usage
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1).isoformat()

    cursor.execute("""
        SELECT COUNT(*) FROM analytics_events
        WHERE user_id = ?
        AND event_type IN ('chat_message_sent', 'research_started', 'analysis_completed')
        AND created_at >= ?
    """, (user_id, start_of_month))

    current_usage = cursor.fetchone()[0]
    print(f"\nCurrent usage this month: {current_usage}")
    print(f"Limit: {'1000' if role == 'admin' else '2'}")

    # Reset if needed
    if current_usage > 0:
        cursor.execute("""
            DELETE FROM analytics_events
            WHERE user_id = ?
            AND created_at >= ?
        """, (user_id, start_of_month))
        conn.commit()
        print(f"\n✓ Reset usage (deleted {cursor.rowcount} events)")
    else:
        print(f"\n✓ Usage already at 0, no reset needed")
else:
    print("User not found")

conn.close()
