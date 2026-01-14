from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.booking import Booking

app = create_app()

with app.app_context():
    email = "driver26@trial.com"
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"User {email} not found.")
    else:
        print(f"User: {user.name} (ID: {user.id}) | Phone: {user.phone_number}")
        print("--- ALL BOOKINGS FOR USER ---")
        bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.id.desc()).all()
        
        if not bookings:
            print("No bookings found for this user.")
        else:
            for b in bookings:
                print(f"ID: {b.id} | Status: {b.status} | MatatuID: {b.matatu_id} | Seat: {b.seat_number} | Created: {b.created_at}")
