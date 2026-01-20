#!/usr/bin/env python3
"""
Feature #211 Test Script - Usage Limit Enforcement
Tests that usage limits are properly enforced for users.
"""
import sqlite3
import sys

# Connect to database
db_path = '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/mi_navigator.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("FEATURE #211 TEST - Usage Limit Enforcement")
print("=" * 70)

# Step 1: Check if test user exists
print("\n[STEP 1] Checking test user...")
cursor.execute("""
    SELECT id, email, role, created_at
    FROM users
    WHERE email = 'testlimit321@test.com'
""")
user = cursor.fetchone()

if not user:
    print("❌ FAIL: Test user 'testlimit321@test.com' not found in database")
    sys.exit(1)

user_id, email, role, created_at = user
print(f"✅ User found:")
print(f"   - ID: {user_id}")
print(f"   - Email: {email}")
print(f"   - Role: {role}")
print(f"   - Created: {created_at}")

# Step 2: Check current usage count
print("\n[STEP 2] Checking current usage count...")
cursor.execute("""
    SELECT COUNT(*)
    FROM analytics_events
    WHERE user_id = ?
    AND event_type IN ('chat_message_sent', 'research_started', 'analysis_completed')
    AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
""", (user_id,))
current_usage = cursor.fetchone()[0]

print(f"✅ Current usage this month: {current_usage}")

# Step 3: Determine expected limit based on role
if role == 'admin':
    expected_limit = 1000
else:
    expected_limit = 2  # From usage_limits.py line 61

print(f"✅ Expected limit for role '{role}': {expected_limit}")

# Step 4: Check if user should be blocked
should_be_blocked = current_usage >= expected_limit
print(f"\n[STEP 3] Should user be blocked? {should_be_blocked}")
print(f"   - Current usage: {current_usage}/{expected_limit}")

if should_be_blocked:
    print(f"   ⚠️  User has reached limit - next message should be BLOCKED")
else:
    remaining = expected_limit - current_usage
    print(f"   ✅ User has {remaining} message(s) remaining")

# Step 5: List all analytics events for this user
print("\n[STEP 4] User's analytics events:")
cursor.execute("""
    SELECT event_type, created_at
    FROM analytics_events
    WHERE user_id = ?
    AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
    ORDER BY created_at DESC
    LIMIT 10
""", (user_id,))
events = cursor.fetchall()

if events:
    for event_type, created in events:
        print(f"   - {event_type}: {created}")
else:
    print("   (No events recorded)")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"User: {email}")
print(f"Role: {role}")
print(f"Limit: {expected_limit}")
print(f"Current Usage: {current_usage}/{expected_limit}")
print(f"Status: {'🔴 BLOCKED' if should_be_blocked else '🟢 ALLOWED'}")
print("=" * 70)

conn.close()
