from app.models.matatu import Matatu
from app.models.booking import Booking
from app.models.user import User
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def try_delete_with_constraint():
    with app.app_context():
        print("--- Reproduction: Delete Vehicle with Booking ---")
        
        # 1. Create a dummy vehicle
        v = Matatu(plate_number="TEST-999", capacity=14, sacco_id=1)
        db.session.add(v)
        db.session.flush() # get ID
        
        # 2. Create a dummy Booking linked to it
        # Need a user first
        u = User.query.first() 
        if not u:
            print("No users found to create booking.")
            return

        b = Booking(seat_number="1A", user_id=u.id, matatu_id=v.id)
        db.session.add(b)
        db.session.commit()
        
        print(f"Created Vehicle {v.id} and Booking {b.id}")

        # 3. Try to delete Vehicle
        try:
            print(f"Attempting delete of Vehicle {v.id}...")
            db.session.delete(v)
            db.session.commit()
            print("SUCCESS: Deleted vehicle (Expected behavior)")
        except Exception as e:
            print(f"FAILURE: Caught unexpected error: {e}")
            db.session.rollback()
            
            # Clean up manually
            print("Cleaning up...")
            b = db.session.get(Booking, b.id)
            if b: db.session.delete(b)
            v = db.session.get(Matatu, v.id)
            if v: db.session.delete(v)
            db.session.commit()

if __name__ == "__main__":
    try_delete_with_constraint()
