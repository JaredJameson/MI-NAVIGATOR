import base64
import json
import datetime

payload = 'eyJzdWIiOiI0YTVhNDdjZi1lMmE2LTRlMTAtYWE5ZC1mN2E3Y2IyMDEzNDIiLCJleHAiOjE3Njg3ODA2OTgsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiIyYzRiMDFhOC00YzEyLTQ1ODgtYjZmOS0wNThmYjgxN2IxOTMifQ'
decoded = base64.b64decode(payload + '==')
data = json.loads(decoded)
print(json.dumps(data, indent=2))
print(f"\nExpires: {datetime.datetime.fromtimestamp(data['exp'])}")
print(f"Now: {datetime.datetime.now()}")
print(f"Expired: {datetime.datetime.fromtimestamp(data['exp']) < datetime.datetime.now()}")
