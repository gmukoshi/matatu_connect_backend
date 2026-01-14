from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.matatu import Matatu
from app.models.booking import Booking
from app.models.payment import Payment

app = create_app()

with app.app_context():
    print("--- DEBUGGING DRIVER: driver25@trial.com ---")
    
    driver = User.query.filter_by(email='driver25@trial.com').first()
    if not driver:
        print("ERROR: Driver not found!")
    else:
        print(f"Driver ID: {driver.id} | Name: {driver.name}")
        
        # Check Vehicle Assignment
        vehicle = Matatu.query.filter_by(driver_id=driver.id).first()
        if not vehicle:
             print("ERROR: No vehicle assigned to this driver!")
        else:
            print(f"Assigned Vehicle: {vehicle.plate_number} (ID: {vehicle.id})")
            
            # Check Bookings for this Vehicle
            bookings = Booking.query.filter_by(matatu_id=vehicle.id).order_by(Booking.id.desc()).all()
            print(f"Total Bookings for Vehicle: {len(bookings)}")
            
            for b in bookings[:5]: # Show top 5
                p = Payment.query.filter_by(booking_id=b.id).first()
                paid_str = f"PAID (Ref: {p.reference}, Amt: {p.amount})" if p else "UNPAID"
                print(f"  Booking {b.id} | Seat {b.seat_number} | Status: {b.status} | Payment: {paid_str}")

    print("------------------------------------------")
