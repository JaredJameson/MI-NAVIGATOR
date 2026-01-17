#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

import pyotp

# Secret from the QR code
secret = "EDNX72EPIB2IX75O3FRMBA6EOPFN5HJD"
totp = pyotp.TOTP(secret)
code = totp.now()
print(f"Current TOTP code: {code}")
print(f"Secret: {secret}")
