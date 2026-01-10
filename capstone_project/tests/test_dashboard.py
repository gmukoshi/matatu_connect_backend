def test_dashboard_stats(client):
    # 1. Populate data
    client.post("/api/matatus/", json={
        "plate_number": "DASH 001",
        "sacco_id": 1,
        "capacity": 14
    })
    
    # 2. Get stats
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    
    data = response.json["data"]
    assert "total_bookings" in data
    assert "active_matatus" in data
    assert "revenue_today" in data
    assert "total_users" in data
    
    # Check values (should be at least 1 matatu)
    assert data["active_matatus"] >= 1
