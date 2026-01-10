from flask_jwt_extended import create_access_token

def test_create_booking(client):
    # 1. Create User
    client.post("/api/auth/register", json={
        "email": "rider@example.com",
        "password": "pass",
        "name": "Rider",
        "role": "commuter"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "rider@example.com",
        "password": "pass"
    })
    token = login_resp.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Route & Matatu (Prerequisites)
    # We need a matatu to book. Matatu needs a route usually, but model allows None. 
    # Let's just create a simple Matatu for now.
    matatu_resp = client.post("/api/matatus/", json={
        "plate_number": "TEST 123",
        "sacco_id": 1
    })
    matatu_id = matatu_resp.json["data"]["id"]

    # 3. Create Booking
    response = client.post("/api/bookings/", json={
        "matatu_id": matatu_id,
        "seat_number": 5
    }, headers=headers)
    
    assert response.status_code == 201
    assert response.json["data"]["matatu"]["id"] == matatu_id
    assert response.json["data"]["status"] == "pending"

def test_get_bookings_commuter(client):
    # 1. Register & Login Commuter
    client.post("/api/auth/register", json={
        "email": "commuter@example.com",
        "password": "pass",
        "name": "Commuter",
        "role": "commuter"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "commuter@example.com",
        "password": "pass"
    })
    token = login_resp.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Bookings (Should be empty initially)
    response = client.get("/api/bookings/", headers=headers)
    assert response.status_code == 200
    assert response.json["data"] == []

def test_get_bookings_admin(client):
    # 1. Register & Login Admin
    # Note: Default register sets role='commuter' if not specified, but request allows override.
    # We trust the auth endpoint allows 'admin' role for testing purposes (or we mock it).
    # Based on auth code: role=data.get("role", "commuter")
    client.post("/api/auth/register", json={
        "email": "admin@example.com",
        "password": "pass",
        "name": "Admin",
        "role": "admin"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "pass"
    })
    token = login_resp.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/bookings/", headers=headers)
    assert response.status_code == 200
