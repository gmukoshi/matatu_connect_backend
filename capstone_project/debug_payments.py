
from app import create_app, db
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.user import User
from app.models.matatu import Matatu

app = create_app()

with app.app_context():
    print("--- PAYMENT DEBUG ---")
    payments = Payment.query.all()
    print(f"Total Payments Found: {len(payments)}")
    
    total_revenue = 0
    for p in payments:
        booking = Booking.query.get(p.booking_id)
        matatu = booking.matatu if booking else None
        sacco_id = matatu.sacco_id if matatu else "N/A"
        plate = matatu.plate_number if matatu else "N/A"
        
        print(f"ID: {p.id} | Status: {p.status} | Amt: {p.amount} | Ref: {p.reference} | Matatu: {plate} (ID: {matatu.id if matatu else '?'}) | Sacco: {sacco_id}")
        
        if p.status == 'completed':
            total_revenue += p.amount
            
    print(f"Calculated Total Revenue (DB): {total_revenue}")
    
    print("\n--- BOOKING STATUS DEBUG ---")
    bookings = Booking.query.filter_by(status='confirmed').all()
    print(f"Confirmed Bookings: {len(bookings)}")
    for b in bookings:
        pay_status = b.payment.status if b.payment else "No Payment Record"
        print(f"Booking {b.id} | Status: {b.status} | Payment Status: {pay_status}")

    print("\n--- SACCO STATS DEBUG ---")
    # Simulate the query from dashboard.py
    from sqlalchemy import func
    revenue_query = db.session.query(func.sum(Payment.amount))\
                .filter(Payment.status == 'completed')\
                .scalar() or 0.0
    print(f"Dashboard Query Result (Global): {revenue_query}")
