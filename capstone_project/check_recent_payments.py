from app import create_app
from app.extensions import db
from app.models.payment import Payment
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("--- RECENT PAYMENTS (Last 1 Hour) ---")
    
    cutoff = datetime.utcnow() - timedelta(hours=1)
    payments = Payment.query.filter(Payment.created_at >= cutoff).order_by(Payment.id.desc()).all()
    
    if not payments:
        print("No payments found in the last hour.")
    else:
        for p in payments:
            print(f"ID: {p.id} | BookingID: {p.booking_id} | UserID: {p.user_id} | Amount: {p.amount} | Ref: {p.reference} | Time: {p.created_at}")

    print("---------------------------------------")
