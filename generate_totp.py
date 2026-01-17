#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

import pyotp

secret = "RWLS2I4IEEDKXZ4T3HWZLZ5ZV5ALACK2"
totp = pyotp.TOTP(secret)
code = totp.now()
print(code)
