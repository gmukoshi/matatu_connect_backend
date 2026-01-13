from app.models.matatu import Matatu
from app.models.booking import Booking
from app.models.user import User
from app.extensions import db
from app.config import Config
from flask import Flask
from app import create_app

def test_endpoint_logic():
    app = create_app()
    
    with app.app_context():
        print("--- Verification: Delete Vehicle via API Logic ---")
        
        # 1. Setup Data
        v = Matatu(plate_number="API-TEST-1", capacity=14, sacco_id=1)
        
        # Cleanup if exists
        existing = Matatu.query.filter_by(plate_number="API-TEST-1").first()
        if existing:
            # Need to delete bookings first due to constraints (ironic, but necessary for setup)
            Booking.query.filter_by(matatu_id=existing.id).delete()
            db.session.delete(existing)
            db.session.commit()
            
        db.session.add(v)
        db.session.flush()
        
        u = User.query.first()
        b = Booking(seat_number="1A", user_id=u.id, matatu_id=v.id)
        db.session.add(b)
        db.session.commit()
        
        v_id = v.id
        print(f"Created Vehicle {v_id} with Booking {b.id}")
        
    # 2. Use Test Client to Call DELETE Endpoint
    with app.test_client() as client:
        print(f"Calling DELETE /api/matatus/{v_id} ...")
        res = client.delete(f"/api/matatus/{v_id}")
        
        if res.status_code == 200:
            print("SUCCESS: Endpoint returned 200 OK")
        else:
            print(f"FAILURE: Endpoint returned {res.status_code}")
            print(res.json)
            return

    # 3. Verify Database
    with app.app_context():
        v_check = db.session.get(Matatu, v_id)
        b_check = Booking.query.filter_by(matatu_id=v_id).first()
        
        if v_check is None and b_check is None:
             print("SUCCESS: Database verified (Vehicle and Bookings gone)")
        else:
             print(f"FAILURE: Database state incorrect. V:{v_check}, B:{b_check}")

if __name__ == "__main__":
    test_endpoint_logic()
