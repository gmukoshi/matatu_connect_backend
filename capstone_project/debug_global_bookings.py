from app import create_app
from app.extensions import db
from app.models.booking import Booking
from app.models.user import User

app = create_app()

with app.app_context():
    print("--- LATEST 10 BOOKINGS GLOBALLY ---")
    bookings = Booking.query.order_by(Booking.id.desc()).limit(10).all()
    
    if not bookings:
        print("No bookings found in the system.")
    else:
        for b in bookings:
            user = User.query.get(b.user_id)
            user_name = user.name if user else "Unknown"
            user_email = user.email if user else "Unknown"
            print(f"ID: {b.id} | User: {user_name} ({user_email}) | Status: {b.status} | Asgn Status: {getattr(b, 'assignment_status', 'N/A')} | Date: {b.booking_date}")
