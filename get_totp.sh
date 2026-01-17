#!/bin/bash
/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/venv/bin/python3 << 'EOF'
import pyotp
secret = "7WTOYNUQ5OS6NTGMDKGJ6BAW5GXEHOT3"
totp = pyotp.TOTP(secret)
print(totp.now())
EOF
