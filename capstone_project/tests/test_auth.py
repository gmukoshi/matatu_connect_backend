from app.models.user import User

def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "commuter"
    })
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"

    # Verify user is in DB
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.name == "Test User"

def test_register_duplicate_email(client):
    # Register first user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "User 1"
    })

    # Try to register same email
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password456",
        "name": "User 2"
    })
    assert response.status_code == 409
    assert "Email already registered" in response.json["error"]

def test_register_missing_fields(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com"
        # Missing password and name
    })
    assert response.status_code == 400

def test_login_success(client):
    # Register first
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "password123",
        "name": "Login User"
    })

    # Login
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json

def test_login_invalid_credentials(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "password123",
        "name": "Login User"
    })

    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
