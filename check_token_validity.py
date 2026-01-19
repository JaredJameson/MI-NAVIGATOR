import jwt
import json
from datetime import datetime

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMTM2NGZkMS0wYjY3LTRkNWYtYTZmZS0xYzg0ZDBiMjIwYTQiLCJleHAiOjE3Njg4NDM4NDYsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiI0ZDM0NDg5YS0wYTRmLTQ1YjItYWQwOC1jYTdlNzE1MzAwYzIifQ.vdk3_42yqOYGx4_vViSfI7SkkpvcjC81vn8tCc6IdWU"

# Decode without verification to see payload
payload = jwt.decode(token, options={"verify_signature": False})
print("Token payload:")
print(json.dumps(payload, indent=2))

exp_timestamp = payload['exp']
exp_datetime = datetime.fromtimestamp(exp_timestamp)
now = datetime.now()

print(f"\nExpiration: {exp_datetime}")
print(f"Current time: {now}")
print(f"Token expired: {now > exp_datetime}")
if now > exp_datetime:
    print(f"Token expired {now - exp_datetime} ago")
else:
    print(f"Time until expiration: {exp_datetime - now}")
