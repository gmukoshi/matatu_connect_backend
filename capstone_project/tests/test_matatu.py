from app.models.matatu import Matatu

def test_get_matatus_empty(client):
    response = client.get("/api/matatus/")
    assert response.status_code == 200
    assert response.json["data"] == []

def test_create_matatu(client):
    response = client.post("/api/matatus/", json={
        "plate_number": "KAA 123A",
        "sacco_id": 1,
        "capacity": 14
    })
    assert response.status_code == 201
    assert response.json["data"]["plate_number"] == "KAA 123A"

def test_create_matatu_missing_fields(client):
    response = client.post("/api/matatus/", json={
        "plate_number": "KBB 456B"
        # Missing sacco_id
    })
    assert response.status_code == 400

def test_get_single_matatu(client):
    # Create first
    post_resp = client.post("/api/matatus/", json={
        "plate_number": "KCC 789C",
        "sacco_id": 1
    })
    matatu_id = post_resp.json["data"]["id"]

    # Get
    response = client.get(f"/api/matatus/{matatu_id}")
    assert response.status_code == 200
    assert response.json["data"]["plate_number"] == "KCC 789C"

def test_update_matatu(client):
    # Create
    post_resp = client.post("/api/matatus/", json={
        "plate_number": "KDD 000D",
        "sacco_id": 1,
        "capacity": 14
    })
    matatu_id = post_resp.json["data"]["id"]

    # Update capacity
    response = client.patch(f"/api/matatus/{matatu_id}", json={
        "capacity": 33
    })
    assert response.status_code == 200
    assert response.json["data"]["capacity"] == 33

def test_delete_matatu(client):
    # Create
    post_resp = client.post("/api/matatus/", json={
        "plate_number": "KEE 111E",
        "sacco_id": 1
    })
    matatu_id = post_resp.json["data"]["id"]

    # Delete
    response = client.delete(f"/api/matatus/{matatu_id}")
    assert response.status_code == 200

    # Verify deleted
    get_resp = client.get(f"/api/matatus/{matatu_id}")
    assert get_resp.status_code == 404
