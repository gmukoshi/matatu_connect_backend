from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.booking import Booking

app = create_app()

with app.app_context():
    email = "Commuter9@trial.com"
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"User {email} not found.")
    else:
        print(f"User: {user.name} (ID: {user.id}) | Phone: {user.phone_number}")
        print("--- LAST BOOKING ---")
        booking = Booking.query.filter_by(user_id=user.id).order_by(Booking.id.desc()).first()
        if booking:
             print(f"ID: {booking.id} | Status: {booking.status} | Booking Date: {booking.booking_date}")
