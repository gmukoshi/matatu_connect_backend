from app import create_app
from app.models.payment import Payment
from app.models.user import User
from app.models.booking import Booking

app = create_app()

with app.app_context():
    receipt = "UAE3X3UCSQ"
    print(f"--- SEARCHING FOR RECEIPT: {receipt} ---")
    payment = Payment.query.filter_by(reference=receipt).first()
    
    if payment:
        print(f"FOUND Payment ID: {payment.id} | Booking ID: {payment.booking_id} | Status: {payment.status}")
        booking = Booking.query.get(payment.booking_id)
        print(f"Linked Booking Status: {booking.status}")
        print(f"Linked User: {booking.user.name} ({booking.user.phone_number})")
    else:
        print("Payment NOT found in DB.")
        
    print("\n--- USER CHECK ---")
    phone = "254713721669"
    user = User.query.filter_by(phone_number=phone).first()
    if user:
        print(f"User found for {phone}: ID {user.id} | Name: {user.name}")
        # Check pending bookings
        pending = Booking.query.filter_by(user_id=user.id, status='pending').all()
        print(f"Pending Bookings: {len(pending)}")
        confirmed = Booking.query.filter_by(user_id=user.id, status='confirmed').all()
        print(f"Confirmed Bookings: {len(confirmed)}")
        for b in confirmed:
            p = Payment.query.filter_by(booking_id=b.id).first()
            print(f"  > Booking {b.id} | Matatu {b.matatu_id} | Payment: {'YES (ID '+str(p.id)+')' if p else 'NO'}")
    else:
        print(f"NO USER found for phone {phone}")

    print("------------------------------------------")
