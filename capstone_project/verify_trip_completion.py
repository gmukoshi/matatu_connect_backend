
import sys
import os

# Ensure app is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.matatu import Matatu
from app.models.booking import Booking

app = create_app()

def verify_trip_completion():
    with app.app_context():
        # Setup Client
        client = app.test_client()

        # 1. Cleaning up previous test data if exists
        driver_email = "driver_test@example.com"
        existing_driver = User.query.filter_by(email=driver_email).first()
        if existing_driver:
            # Unassign from any matatus first
            Matatu.query.filter_by(driver_id=existing_driver.id).update({"driver_id": None})
            db.session.commit()
            # Now delete
            User.query.filter_by(email=driver_email).delete()
            db.session.commit()

        # Create Driver
        client.post("/api/auth/register", json={
            "email": driver_email,
            "password": "password123",
            "name": "Test Driver",
            "role": "driver"
        })
        driver_res = client.post("/api/auth/login", json={
            "email": driver_email,
            "password": "password123"
        })
        driver_token = driver_res.json['access_token']
        driver_user = User.query.filter_by(email=driver_email).first()

        # 2. Setup Vehicle & Assign Driver (Hack: Direct DB assignment for speed)
        matatu = Matatu.query.first()
        if not matatu:
            print("No matatu found")
            return
        
        # Unassign previous driver just in case
        matatu.driver_id = driver_user.id
        db.session.commit()
        print(f"Driver {driver_user.name} assigned to Matatu {matatu.id}")

        # 3. Setup Commuter & Booking
        commuter_email = "commuter_test@example.com"
        existing_commuter = User.query.filter_by(email=commuter_email).first()
        if existing_commuter:
             # Delete bookings first
             Booking.query.filter_by(user_id=existing_commuter.id).delete()
             db.session.commit()
             # Delete user
             User.query.filter_by(email=commuter_email).delete()
             db.session.commit()

        client.post("/api/auth/register", json={
            "email": commuter_email,
            "password": "password123",
            "name": "Test Commuter",
            "role": "commuter"
        })
        commuter_res = client.post("/api/auth/login", json={
            "email": commuter_email,
            "password": "password123"
        })
        commuter_token = commuter_res.json['access_token']

        # Create Booking
        print("Creating booking...")
        b_res = client.post("/api/bookings/", json={
            "matatu_id": matatu.id,
            "seat_number": "1A"
        }, headers={"Authorization": f"Bearer {commuter_token}"})
        
        booking_id = b_res.json['data']['id']

        # Driver Confirms Booking
        print("Driver confirming booking...")
        client.post(f"/api/bookings/{booking_id}/accept", headers={"Authorization": f"Bearer {driver_token}"})
        
        # Verify status is confirmed
        booking = db.session.get(Booking, booking_id)
        print(f"Booking status before completion: {booking.status}")

        # 4. Driver Completes Trip
        print("Driver completing trip...")
        complete_res = client.post("/api/bookings/complete_trip", headers={"Authorization": f"Bearer {driver_token}"})
        
        if complete_res.status_code == 200:
            print("SUCCESS: Trip completion request successful.")
            print("Response:", complete_res.json)
        else:
            print("FAILED: Trip completion failed.")
            print("Response:", complete_res.json)
            return

        # 5. Verify Booking Status
        db.session.refresh(booking)
        print(f"Booking status after completion: {booking.status}")
        
        if booking.status == 'completed':
            print("VERIFICATION PASSED: Booking status updated to 'completed'")
        else:
            print("VERIFICATION FAILED: Booking status mismatch")

if __name__ == "__main__":
    verify_trip_completion()
