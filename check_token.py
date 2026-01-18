import jwt
import datetime

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZGUyNDNkMS1hN2E5LTQ0YzUtYjI4YS03NzJlY2U3ZDUwMGUiLCJleHAiOjE3Njg3NDI5MDcsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiJjMDk3MjMxZS0yNGZhLTQxYjYtYmFhZi1iMzYxN2E3N2I1ZTkifQ.xcxZjBPe9xTrTg_3Q9ih110lOKXJCjXRCWnQjw-9tIg'

decoded = jwt.decode(token, options={'verify_signature': False})
exp_time = datetime.datetime.fromtimestamp(decoded['exp'])
now = datetime.datetime.now()

print(f'Token expires: {exp_time}')
print(f'Current time: {now}')
print(f'Expired: {now > exp_time}')
print(f'User ID: {decoded.get("sub")}')
