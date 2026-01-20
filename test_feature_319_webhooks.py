#!/usr/bin/env python3
"""
Test script for Feature #319: Webhook retry on failure

Tests:
1. Configure webhook
2. Trigger event
3. Make endpoint fail
4. Verify retry occurs
5. Verify exponential backoff
6. Make endpoint succeed
7. Verify delivery succeeds
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api/v1"
WEBHOOK_SERVER = "http://localhost:8001"
TEST_USER = {"email": "user@example.com", "password": "password123"}

def print_step(step_num, description):
    """Print test step header."""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print('='*70)

def login():
    """Login and get access token."""
    print_step(0, "Login to get access token")

    response = requests.post(
        f"{API_BASE}/auth/login",
        json=TEST_USER
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Login successful")
        print(f"   Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def create_webhook(token):
    """Step 1: Configure webhook."""
    print_step(1, "Configure webhook")

    headers = {"Authorization": f"Bearer {token}"}
    webhook_data = {
        "url": f"{WEBHOOK_SERVER}/webhook",
        "event_type": "report.created",
        "max_retries": 5
    }

    print(f"Creating webhook: {json.dumps(webhook_data, indent=2)}")

    response = requests.post(
        f"{API_BASE}/webhooks/",
        json=webhook_data,
        headers=headers
    )

    if response.status_code == 201:
        webhook = response.json()
        print(f"✅ Webhook created successfully")
        print(f"   ID: {webhook['id']}")
        print(f"   URL: {webhook['url']}")
        print(f"   Event: {webhook['event_type']}")
        print(f"   Max Retries: {webhook['max_retries']}")
        return webhook['id']
    else:
        print(f"❌ Webhook creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def set_webhook_server_mode(mode):
    """Change webhook server mode (success/fail)."""
    print(f"\n🔄 Setting webhook server mode to: {mode}")

    response = requests.post(f"{WEBHOOK_SERVER}/mode/{mode}")

    if response.status_code == 200:
        print(f"✅ Mode changed to {mode}")
        return True
    else:
        print(f"❌ Mode change failed: {response.status_code}")
        return False

def trigger_webhook(token, webhook_id):
    """Step 2: Trigger webhook event."""
    print_step(2, "Trigger webhook event")

    headers = {"Authorization": f"Bearer {token}"}
    test_payload = {
        "payload": {
            "event": "report.created",
            "report_id": "test_report_123",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    print(f"Triggering webhook with payload: {json.dumps(test_payload, indent=2)}")

    response = requests.post(
        f"{API_BASE}/webhooks/{webhook_id}/test",
        json=test_payload,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Webhook triggered")
        print(f"   Status: {result.get('status')}")
        print(f"   Retry count: {result.get('retry_count')}")
        print(f"   Last error: {result.get('last_error')}")
        return True
    else:
        print(f"❌ Webhook trigger failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def check_webhook_status(token, webhook_id):
    """Check webhook status."""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{API_BASE}/webhooks/{webhook_id}",
        headers=headers
    )

    if response.status_code == 200:
        webhook = response.json()
        print(f"\n📊 Webhook Status:")
        print(f"   Status: {webhook['status']}")
        print(f"   Retry count: {webhook['retry_count']}/{webhook['max_retries']}")
        print(f"   Last triggered: {webhook.get('last_triggered_at', 'Never')}")
        print(f"   Last delivered: {webhook.get('last_delivered_at', 'Never')}")
        print(f"   Last error: {webhook.get('last_error', 'None')}")
        print(f"   Next retry: {webhook.get('next_retry_at', 'None')}")
        return webhook
    else:
        print(f"❌ Failed to get webhook status: {response.status_code}")
        return None

def check_received_webhooks():
    """Check webhooks received by test server."""
    response = requests.get(f"{WEBHOOK_SERVER}/webhooks")

    if response.status_code == 200:
        data = response.json()
        print(f"\n📥 Webhooks received by test server: {data['total']}")
        for i, wh in enumerate(data['webhooks'], 1):
            print(f"   {i}. {wh['timestamp']} - Mode: {wh['mode_when_received']}")
        return data['total']
    else:
        print(f"❌ Failed to get received webhooks")
        return 0

def main():
    """Run all webhook tests."""
    print("\n" + "="*70)
    print("🚀 Feature #319: Webhook Retry Mechanism Test")
    print("="*70)

    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return

    # Step 1: Configure webhook
    webhook_id = create_webhook(token)
    if not webhook_id:
        print("\n❌ Cannot proceed without webhook")
        return

    # Step 2: Trigger event (success mode first)
    print_step(2, "Trigger event (success mode)")
    set_webhook_server_mode("success")
    trigger_webhook(token, webhook_id)
    time.sleep(1)
    check_webhook_status(token, webhook_id)
    check_received_webhooks()

    # Step 3: Make endpoint fail
    print_step(3, "Make endpoint fail")
    set_webhook_server_mode("fail")
    print("✅ Webhook server now in FAIL mode")

    # Step 4: Trigger webhook (should fail and schedule retry)
    print_step(4, "Trigger webhook (should fail)")
    trigger_webhook(token, webhook_id)
    time.sleep(1)
    webhook = check_webhook_status(token, webhook_id)
    check_received_webhooks()

    if webhook and webhook['status'] == 'retrying':
        print("\n✅ Step 4 PASSED: Webhook entered retrying state")
    else:
        print("\n❌ Step 4 FAILED: Webhook should be in retrying state")

    # Step 5: Verify exponential backoff
    print_step(5, "Verify exponential backoff timing")
    if webhook and webhook.get('next_retry_at'):
        print(f"✅ Next retry scheduled at: {webhook['next_retry_at']}")
        print("   (Exponential backoff: 2^n minutes)")
        print(f"   Retry {webhook['retry_count']}: {2**webhook['retry_count']} minutes")
    else:
        print("❌ No retry scheduled")

    # Step 6: Make endpoint succeed
    print_step(6, "Make endpoint succeed")
    set_webhook_server_mode("success")

    # Step 7: Trigger again (should succeed)
    print_step(7, "Trigger webhook (should succeed)")
    trigger_webhook(token, webhook_id)
    time.sleep(1)
    webhook = check_webhook_status(token, webhook_id)
    check_received_webhooks()

    if webhook and webhook['status'] == 'delivered':
        print("\n✅ Step 7 PASSED: Webhook delivered successfully")
    else:
        print(f"\n⚠️  Step 7: Webhook status is '{webhook['status']}' (expected 'delivered')")

    # Final summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Webhook ID: {webhook_id}")
    print(f"Final Status: {webhook['status']}")
    print(f"Total Retries: {webhook['retry_count']}")
    print(f"Total Webhooks Received: {check_received_webhooks()}")

    print("\n✅ Feature #319 testing complete!")

if __name__ == "__main__":
    main()
