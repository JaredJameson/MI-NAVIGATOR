import pyotp
secret = "7WTOYNUQ5OS6NTGMDKGJ6BAW5GXEHOT3"
totp = pyotp.TOTP(secret)
print(totp.now())
