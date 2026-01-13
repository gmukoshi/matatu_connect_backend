import requests
from app import create_app
from app.models.user import User

def debug_driver_fetch():
    # URL = "http://localhost:5000/api/users/manager/drivers"
    # Instead of requests which might fail from inside container environment setup 
    # (though user has server running), I'll use test client for direct app context access
    
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            # 1. Find a manager
            manager = User.query.filter_by(role='sacco_manager').first()
            if not manager:
                print("No manager found!")
                return
                
            print(f"Testing with Manager: {manager.name} (ID: {manager.id}, Sacco: {manager.sacco_id})")

            # 2. Login
            login_res = client.post("/api/auth/login", json={
                "email": manager.email,
                "password": "pass" # Assuming test password 'pass' based on previous context/seed
                # If password fails, I might need to reset it or just assume I can mock identity
            })
            
            if login_res.status_code != 200:
                # User might have real password. Let's try to mock the JWT token directly or force login
                # Actually, I can just use create_access_token if I import it
                from flask_jwt_extended import create_access_token
                token = create_access_token(identity={"id": manager.id, "role": manager.role})
                print("Generated Test Token manually.")
            else:
                token = login_res.json['access_token']
                print("Logged in successfully.")

            # 3. Fetch Drivers
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Fetching /api/users/manager/drivers...")
            res = client.get("/api/users/manager/drivers", headers=headers)
            
            print(f"Status Code: {res.status_code}")
            print(f"Response Data: {res.json}")
            
            if res.status_code == 200:
                data = res.json
                print(f"Type of data: {type(data)}")
                if isinstance(data, list):
                    print(f"Count: {len(data)}")
                else:
                    print("Data is not a list!")

if __name__ == "__main__":
    debug_driver_fetch()
