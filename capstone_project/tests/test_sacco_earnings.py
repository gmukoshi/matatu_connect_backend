from app.models.booking import Booking
from app.models.matatu import Matatu
from app.models.user import User
from app.models.payment import Payment
from app.extensions import db

def test_sacco_earnings_aggregation(client):
    # 1. Setup: Sacco Manager, Driver, Matatu
    # Sacco ID = 99
    
    # Manager
    res = client.post("/api/auth/register", json={
        "email": "manager_rev@test.com", "password": "pass", 
        "name": "Manager Revenue", "role": "sacco_manager"
    })
    manager_token = res.json["access_token"]
    manager_id = res.json["user"]["id"]
    
    # Assign Manager to Sacco 99 manually (since register doesn't do it)
    manager = db.session.get(User, manager_id)
    manager.sacco_id = 99
    db.session.commit()

    # Driver (same sacco)
    res = client.post("/api/auth/register", json={
        "email": "driver_rev@test.com", "password": "pass", 
        "name": "Driver Rev", "role": "driver", "licence": "DL-REV"
    })
    driver_id = res.json["user"]["id"]
    
    # Matatu (same sacco)
    matatu = Matatu(plate_number="REV 999K", capacity=14, driver_id=driver_id, sacco_id=99)
    db.session.add(matatu)
    db.session.commit()
    
    # Commuter
    res = client.post("/api/auth/register", json={
        "email": "commuter_rev@test.com", "password": "pass", "name": "Commuter Rev"
    })
    commuter_token = res.json["access_token"]
    commuter_id = res.json["user"]["id"]
    
    # 2. Setup: Bookings & Payments
    # Booking 1: Completed Payment (500)
    b1 = Booking(user_id=commuter_id, matatu_id=matatu.id, seat_number="1A", status="confirmed")
    db.session.add(b1)
    db.session.commit()
    
    p1 = Payment(booking_id=b1.id, user_id=commuter_id, amount=500.0, status='completed', method='mpesa', reference="MPESA001")
    db.session.add(p1)
    
    # Booking 2: Pending Payment (Should not count)
    b2 = Booking(user_id=commuter_id, matatu_id=matatu.id, seat_number="1B", status="confirmed")
    db.session.add(b2)
    db.session.commit()
    
    p2 = Payment(booking_id=b2.id, user_id=commuter_id, amount=300.0, status='pending', method='mpesa', reference="MPESA002")
    db.session.add(p2)
    
    # Booking 3: Different Sacco (Should not count)
    # create matatu sacco 100
    matatu2 = Matatu(plate_number="OTH 100K", capacity=14, driver_id=None, sacco_id=100)
    db.session.add(matatu2)
    db.session.commit()
    
    b3 = Booking(user_id=commuter_id, matatu_id=matatu2.id, seat_number="1A", status="confirmed")
    db.session.add(b3)
    db.session.commit()
    
    p3 = Payment(booking_id=b3.id, user_id=commuter_id, amount=1000.0, status='completed', method='mpesa', reference="MPESA003")
    db.session.add(p3)
    
    db.session.commit()
    
    # 3. Call Endpoint as Manager
    res = client.get("/api/dashboard/sacco-stats", headers={"Authorization": f"Bearer {manager_token}"})
    
    # 4. Assertions
    assert res.status_code == 200
    data = res.json["data"]
    # Total should be 500 (p1 only)
    # p2 is pending, p3 is different sacco
    assert data["total_revenue"] == 500.0
