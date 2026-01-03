from app.extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matatu_id = db.Column(db.Integer, db.ForeignKey('matatus.id'), nullable=False)
    
    # Relationships
    # Backref allows us to do: user.bookings or matatu.bookings
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    matatu = db.relationship('Matatu', backref=db.backref('bookings', lazy=True))
    
    # One-to-One relationship with Payment
    payment = db.relationship('Payment', backref='booking', uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        """Helper for serialization without Marshmallow"""
        return {
            "id": self.id,
            "seat_number": self.seat_number,
            "status": self.status,
            "booking_date": self.booking_date.isoformat(),
            "user_id": self.user_id,
            "matatu": {
                "id": self.matatu.id,
                "plate": self.matatu.registration_number,
                "sacco": self.matatu.sacco_name
            },
            "payment": {
                "status": self.payment.status if self.payment else "not_initiated",
                "amount": self.payment.amount if self.payment else 0,
                "receipt": self.payment.mpesa_receipt_number if self.payment else None
            }
        }