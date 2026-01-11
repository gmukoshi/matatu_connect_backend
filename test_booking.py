import requests
import sys

BASE_URL = "http://localhost:5000/api"
EMAIL = "commuter1@example.com"
PASSWORD = "password"

# 0. Register (ignore if exists)
try:
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD, "name": "Commuter Test", "role": "commuter"})
except:
    pass

# 1. Login
try:
    auth_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    auth_resp.raise_for_status()
    token = auth_resp.json().get("access_token")
    print(f"Token acquired. Length: {len(token)}")
except Exception as e:
    print(f"Login failed: {e}")
    if 'auth_resp' in locals():
        print(auth_resp.text)
    sys.exit(1)

# 2. Create Booking
try:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"matatu_id": 1, "seat_number": 3}
    print(f"Sending booking payload: {payload}")
    
    resp = requests.post(f"{BASE_URL}/bookings/", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    resp.raise_for_status()
    print("Booking success!")
except Exception as e:
    print(f"Booking failed: {e}")
