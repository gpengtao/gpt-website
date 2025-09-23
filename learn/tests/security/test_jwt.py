import jwt
import json
from datetime import datetime

# 你的token（去掉Bearer前缀）
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjNhNDYyMTQtNDYwNS00NjEzLWE3Y2ItZWJhMTc0ODc3MTAyIiwiZXhwIjoxNzU4NjIwNjAyLCJpc3MiOiJTRUxGX0hPU1RFRCIsInN1YiI6IkNvbnNvbGUgQVBJIFBhc3Nwb3J0In0.rdl15T84OhswwGuSU-lbFJuh7HHop-h2ijAdnSO0vU0"

# 解码payload（不需要密钥）
payload = jwt.decode(token, options={"verify_signature": False})
print("Token payload:", json.dumps(payload, indent=2))

# 检查过期时间
exp_timestamp = payload.get('exp')
if exp_timestamp:
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    current_time = datetime.now()
    print(f"Token expires at: {exp_datetime}")
    print(f"Current time: {current_time}")
    print(f"Token expired: {current_time > exp_datetime}")