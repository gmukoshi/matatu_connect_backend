from app.models.log import MatatuLog
from app.models.matatu import Matatu
from app.models.user import User
from app.extensions import db
from datetime import date

def test_fleet_stats_workflow(client):
    # 1. Setup Data
    # Sacco ID = 800
    
    # Manager
    res = client.post("/api/auth/register", json={
        "email": "manager_stats@test.com", "password": "pass", "name": "Manager Stats", "role": "sacco_manager"
    })
    manager_token = res.json["access_token"]
    manager_id = res.json["user"]["id"]
    
    manager = db.session.get(User, manager_id)
    manager.sacco_id = 800
    db.session.commit()
    
    # Driver 1 (Active)
    res = client.post("/api/auth/register", json={
        "email": "driver_stats1@test.com", "password": "pass", "name": "Driver Stats 1", "role": "driver", "licence": "DL-S1"
    })
    driver1_token = res.json["access_token"]
    driver1_id = res.json["user"]["id"]
    
    # Driver 2 (Assigned but no logs today)
    res = client.post("/api/auth/register", json={
        "email": "driver_stats2@test.com", "password": "pass", "name": "Driver Stats 2", "role": "driver", "licence": "DL-S2"
    })
    driver2_id = res.json["user"]["id"]

    # Matatu 1 (Active)
    m1 = Matatu(plate_number="KAA 555K", capacity=14, driver_id=driver1_id, sacco_id=800, assignment_status="active")
    db.session.add(m1)
    
    # Matatu 2 (Active)
    m2 = Matatu(plate_number="KBB 333L", capacity=14, driver_id=driver2_id, sacco_id=800, assignment_status="active")
    db.session.add(m2)
    
    # Matatu 3 (Pending - Shouldn't count as active?)
    # Our logic in dashboard.py: assignment_status='active'
    m3 = Matatu(plate_number="KCC 111J", capacity=14, driver_id=None, sacco_id=800, assignment_status="pending")
    db.session.add(m3)
    
    db.session.commit()
    
    # 2. Driver 1 Submits Log
    log_data = {
        "passengers": 120,
        "fuel": 30.0,
        "mileage": 150.0
    }
    
    res = client.post("/api/logs/", json=log_data, headers={"Authorization": f"Bearer {driver1_token}"})
    assert res.status_code == 201
    assert res.json["data"]["passengers"] == 120
    
    # 3. Manager Fetches Stats
    res = client.get("/api/dashboard/sacco-stats", headers={"Authorization": f"Bearer {manager_token}"})
    assert res.status_code == 200
    data = res.json["data"]
    
    # Checks
    # Active Fleet: m1 and m2 are active. m3 is pending.
    # Logic: Matatu.query.filter_by(sacco_id=sacco_id, assignment_status='active').count()
    # Expected: 2/3
    assert data["active_fleet"] == "2/3"
    
    # Daily Passengers: 120 (from m1)
    assert data["daily_passengers"] == 120
    
    # Fuel Efficiency: 150km / 30L = 5.0 km/L
    assert data["fuel_efficiency"] == "5.0 km/L"
