from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.payment import Payment

app = create_app()

with app.app_context():
    email = "driver26@trial.com"
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"User {email} not found.")
    else:
        print(f"User: {user.name} (ID: {user.id})")
        print("--- ALL PAYMENTS FOR USER ---")
        payments = Payment.query.filter_by(user_id=user.id).order_by(Payment.created_at.desc()).all()
        
        if not payments:
            print("No payments found for this user.")
        else:
            for p in payments:
                print(f"ID: {p.id} | Amount: {p.amount} | Status: {p.status} | Ref: {p.reference} | Method: {p.method} | Time: {p.created_at}")
