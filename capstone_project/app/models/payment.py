from datetime import datetime
from ..extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False)  # mpesa, card, cash
    status = db.Column(db.String(30), default="pending")  # pending, completed, failed
    reference = db.Column(db.String(100), unique=True) # Mpesa Receipt Number

    checkout_request_id = db.Column(db.String(100), unique=True, nullable=True)
    merchant_request_id = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status,
            "reference": self.reference,
            "checkout_request_id": self.checkout_request_id,
            "created_at": self.created_at.isoformat()
        }
