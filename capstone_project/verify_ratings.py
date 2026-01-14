
import sys
import os

# Ensure app is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.matatu import Matatu
from app.models.rating import Rating

app = create_app()

def verify_ratings():
    with app.app_context():
        # Setup Client
        client = app.test_client()

        # 1. Register & Login User
        email = "rater@example.com"
        password = "password123"
        
        # Cleanup first
        User.query.filter_by(email=email).delete()
        db.session.commit()

        print(f"Registering user {email}...")
        client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "name": "Rater User",
            "role": "commuter"
        })

        print("Logging in...")
        res = client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })
        if res.status_code != 200:
            print("Login failed:", res.json)
            return
        
        token = res.json['access_token']
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Find or Create Matatu
        matatu = Matatu.query.first()
        if not matatu:
            print("No matatus found. Cannot test rating.")
            # Create a dummy matatu if needed, but assuming DB has seed
            return
        
        print(f"Rating Matatu ID {matatu.id} ({matatu.plate_number})...")

        # 3. Submit Rating
        rating_data = {
            "matatu_id": matatu.id,
            "score": 5,
            "comment": "Fast and safe!"
        }
        res = client.post("/api/ratings/", json=rating_data, headers=headers)
        
        if res.status_code == 201:
            print("SUCCESS: Rating submitted.")
            print("Response:", res.json)
        else:
            print("FAILED: Rating submission failed.")
            print("Response:", res.json)
            return

        # 4. Fetch Ratings (as user)
        print("Fetching ratings...")
        res = client.get("/api/ratings/", headers=headers)
        if res.status_code == 200:
            ratings = res.json.get('data', [])
            print(f"Found {len(ratings)} ratings.")
            found = any(r['comment'] == "Fast and safe!" for r in ratings)
            if found:
                print("SUCCESS: Verified rating in list.")
            else:
                print("FAILED: Rating not found in list.")
        else:
            print("FAILED: Could not fetch ratings.")

if __name__ == "__main__":
    verify_ratings()
