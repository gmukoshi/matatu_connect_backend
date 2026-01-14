from app import create_app
from app.models.user import User
from app.models.booking import Booking

app = create_app()

def log_debug(msg):
    print(f"LOG: {msg}")

with app.app_context():
    phone_number = "254713721669"
    print(f"--- SIMULATING MATCHING FOR {phone_number} ---")
    
    try:
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            log_debug(f"User matched: {user.name} (ID: {user.id})")
        else:
            if phone_number.startswith('254'):
                alt_phone = '0' + phone_number[3:]
                user = User.query.filter_by(phone_number=alt_phone).first()
                if user: log_debug(f"User matched via alt phone: {user.name} (ID: {user.id})")
        
        booking = None
        if user:
            booking = Booking.query.filter_by(user_id=user.id).filter(
                Booking.status.in_(['pending', 'confirmed'])
            ).order_by(Booking.id.desc()).first()
            
            if booking:
                log_debug(f"Initial booking found: ID {booking.id} | Status: {booking.status} | HasPayment: {bool(booking.payment)}")
            else:
                log_debug("No initial booking found for user.")

            if booking and booking.payment:
                 log_debug(f"Booking {booking.id} already paid. Searching for older unpaid...")
                 booking = Booking.query.filter_by(user_id=user.id).filter(
                    Booking.status.in_(['pending', 'confirmed'])
                 ).filter(~Booking.payment.has()).order_by(Booking.id.desc()).first()
                 if booking:
                     log_debug(f"Fallback booking found: {booking.id}")
                 else:
                     log_debug("No fallback booking found.")

        if not booking:
            log_debug(f"FAILED TO LINK: Phone {phone_number}. User: {user}")
        else:
            log_debug(f"SUCCESS! Linked to Booking {booking.id}")
            
    except Exception as e:
        import traceback
        print(f"CRASHED: {e}")
        print(traceback.format_exc())
