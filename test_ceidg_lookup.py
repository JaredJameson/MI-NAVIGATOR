#!/usr/bin/env python3
"""Test CEIDG lookup functionality"""

import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.api.v1.endpoints.chat import process_chat_message
import json

# Test CEIDG lookup
message = "Lookup company with NIP: 9876543211"
print(f"Testing: {message}\n")

result = process_chat_message(message)
print("Response:")
print(result)

# Parse and pretty print
try:
    data = json.loads(result)
    print("\n\nParsed JSON:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    pass
