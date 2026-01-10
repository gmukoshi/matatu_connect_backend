def test_get_routes_empty(client):
    response = client.get("/api/routes/")
    assert response.status_code == 200
    assert response.json["data"] == []

def test_create_route(client):
    response = client.post("/api/routes/", json={
        "origin": "Nairobi",
        "destination": "Mombasa",
        "fare": 1500,
        "distance": 480,
        "estimated_duration": "8 hours"
    })
    assert response.status_code == 201
    assert response.json["data"]["origin"] == "Nairobi"
    assert response.json["data"]["fare"] == 1500

def test_create_route_integration(client):
    # Create a route and then check list
    client.post("/api/routes/", json={
        "origin": "Thika",
        "destination": "Nairobi",
        "fare": 100
    })
    response = client.get("/api/routes/")
    assert len(response.json["data"]) == 1
    assert response.json["data"][0]["origin"] == "Thika"
