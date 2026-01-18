#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

import pyotp

# Secret from the current 2FA setup
secret = "7HYHKJAWGQRUGVBQVZX7ND4S2BQAWHVY"
totp = pyotp.TOTP(secret)
code = totp.now()
print(code)
