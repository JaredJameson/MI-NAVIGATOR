#!/usr/bin/env python3
"""
Test script to generate a share link with short expiration (5 seconds).
This will temporarily modify the backend to create an expiring link.
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"
TOKEN = None  # Will be set after login

# Step 1: Login to get auth token
def login():
    global TOKEN
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "email": "test2fa@example.com",
            "password": "Test123!"
        }
    )
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print(f"✅ Logged in successfully")
        return True
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False

# Step 2: Generate share link (backend uses 30 day expiration by default)
def generate_share_link():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(
        f"{API_BASE}/reports/report_001/share",
        headers=headers,
        json={"password": None}
    )
    if response.status_code == 200:
        data = response.json()
        share_token = data["share_token"]
        share_url = data["share_url"]
        print(f"✅ Share link generated: {share_url}")
        print(f"   Token: {share_token}")
        print(f"   Expires at: {data['expires_at']}")
        return share_token
    else:
        print(f"❌ Share link generation failed: {response.status_code} - {response.text}")
        return None

# Step 3: Print instructions for manual modification
def print_instructions(share_token):
    # Calculate expiration time (current time + 5 seconds)
    expires_at = (datetime.now() + timedelta(seconds=5)).isoformat() + "Z"

    print("\n" + "="*80)
    print("INSTRUCTIONS TO MANUALLY SET EXPIRATION:")
    print("="*80)
    print("\n1. The backend stores share links in memory in the SHARE_LINKS dict")
    print("2. To test expiration, we need to manually modify the expires_at field")
    print(f"\n3. Share token: {share_token}")
    print(f"4. New expiration time (5 seconds from now): {expires_at}")
    print("\n5. Since we can't modify memory from outside, we'll create a helper endpoint")
    print("="*80)

if __name__ == "__main__":
    print("Share Link Expiration Test Script")
    print("-" * 80)

    if login():
        share_token = generate_share_link()
        if share_token:
            print_instructions(share_token)
            print(f"\n✅ Share token for testing: {share_token}")
            print(f"   URL: http://localhost:3000/share/{share_token}")
