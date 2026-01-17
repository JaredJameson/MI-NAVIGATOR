#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

import pyotp

# New secret from the 2FA setup dialog
secret = "7WTOYNUQ5OS6NTGMDKGJ6BAW5GXEHOT3"
totp = pyotp.TOTP(secret)
code = totp.now()
print(f"Current TOTP code: {code}")
print(f"Secret: {secret}")
