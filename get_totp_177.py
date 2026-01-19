#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')
import pyotp

secret = "GHGOJLDOTNUXFPKMOWF4AKF5O3RQYHBJ"
totp = pyotp.TOTP(secret)
code = totp.now()
print(code)
