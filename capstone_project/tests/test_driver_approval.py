from app.models.user import User
from app.extensions import db

def test_driver_signup_verification_flow(client):
    # 1. Register Driver
    driver_data = {
        "email": "driver@test.com",
        "password": "pass",
        "name": "Driver Test",
        "role": "driver",
        "licence": "DL-123"
    }
    res = client.post("/api/auth/register", json=driver_data)
    assert res.status_code == 201
    driver_id = res.json["user"]["id"]
    
    # Verify DB state
    driver_user = User.query.get(driver_id)
    assert driver_user.verification_status == "pending"
    assert driver_user.license_number == "DL-123"

    # 2. Register Manager
    manager_data = {
        "email": "manager@test.com",
        "password": "pass",
        "name": "Manager Test",
        "role": "sacco_manager"
    }
    client.post("/api/auth/register", json=manager_data)

    # 3. Login Manager
    res = client.post("/api/auth/login", json={"email": "manager@test.com", "password": "pass"})
    token = res.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Approve Driver
    res = client.post(f"/api/users/manager/drivers/{driver_id}/approve", headers=headers)
    assert res.status_code == 200
    assert res.json["data"]["verification_status"] == "approved"

    # 5. Verify DB state again
    db.session.expire_all() # Ensure fresh data
    driver_user = User.query.get(driver_id)
    assert driver_user.verification_status == "approved"

def test_driver_signup_rejection(client):
    # 1. Register Driver
    res = client.post("/api/auth/register", json={
        "email": "reject@test.com", "password": "pass", "name": "Reject Me", "role": "driver", "licence": "DL-FAIL"
    })
    driver_id = res.json["user"]["id"]

    # 2. Register & Login Manager
    client.post("/api/auth/register", json={
        "email": "manager2@test.com", "password": "pass", "name": "Manager 2", "role": "sacco_manager"
    })
    token = client.post("/api/auth/login", json={"email": "manager2@test.com", "password": "pass"}).json["access_token"]

    # 3. Reject Driver
    res = client.post(f"/api/users/manager/drivers/{driver_id}/reject", headers={"Authorization": f"Bearer {token}"}, json={})
    assert res.status_code == 200
    assert res.json["data"]["verification_status"] == "rejected"
