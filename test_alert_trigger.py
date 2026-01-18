#!/usr/bin/env python3
"""
Test alert trigger for Feature #71
"""
import requests
import json

# Test user credentials
EMAIL = "test2fa@example.com"
PASSWORD = "TestPass123!"

BASE_URL = "http://localhost:8000/api/v1"

def main():
    # 1. Login to get token
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return

    token = login_response.json()["access_token"]
    print(f"✓ Login successful, token: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get current alert configs
    print("\n2. Getting alert configurations...")
    configs_response = requests.get(f"{BASE_URL}/alerts/configs", headers=headers)
    configs = configs_response.json()
    print(f"✓ Found {configs['total']} alert config(s)")

    for config in configs['items']:
        print(f"  - {config['company_name']} ({config['alert_type']})")

    # 3. Get current alerts (before trigger)
    print("\n3. Getting alerts before trigger...")
    alerts_before = requests.get(f"{BASE_URL}/alerts/", headers=headers)
    alerts_before_data = alerts_before.json()
    print(f"✓ Current alerts: {alerts_before_data['total']}")
    print(f"✓ Unread: {alerts_before_data['unread_count']}")

    # 4. Trigger alert for TechCorp
    print("\n4. Triggering alert for TechCorp...")
    trigger_response = requests.post(
        f"{BASE_URL}/alerts/trigger",
        headers=headers,
        json={
            "company_name": "TechCorp",
            "event_type": "news_mention",
            "event_description": "TechCorp ogłasza nową rundę finansowania w wysokości 5M PLN"
        }
    )

    if trigger_response.status_code != 200:
        print(f"✗ Trigger failed: {trigger_response.text}")
        return

    trigger_result = trigger_response.json()
    print(f"✓ Trigger successful!")
    print(f"  - Notifications generated: {trigger_result['notifications_generated']}")
    print(f"  - Message: {trigger_result['message']}")

    # 5. Get alerts after trigger
    print("\n5. Getting alerts after trigger...")
    alerts_after = requests.get(f"{BASE_URL}/alerts/", headers=headers)
    alerts_after_data = alerts_after.json()
    print(f"✓ Current alerts: {alerts_after_data['total']}")
    print(f"✓ Unread: {alerts_after_data['unread_count']}")

    # 6. Show new alerts
    if alerts_after_data['total'] > alerts_before_data['total']:
        print("\n6. New alert(s) created:")
        for alert in alerts_after_data['items'][:1]:  # Show first one
            print(f"  ID: {alert['id']}")
            print(f"  Title: {alert['title']}")
            print(f"  Description: {alert['description']}")
            print(f"  Severity: {alert['severity']}")
            print(f"  Company: {alert['company']}")
            print(f"  Read: {alert['read']}")
    else:
        print("\n6. No new alerts created (check if alert config exists for TechCorp)")

if __name__ == "__main__":
    main()
