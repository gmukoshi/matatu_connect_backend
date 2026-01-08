from app.extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matatu_id = db.Column(db.Integer, db.ForeignKey('matatus.id'), nullable=False)
    
    # Standardized relationships
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    matatu = db.relationship('Matatu', backref=db.backref('bookings', lazy=True))
    
    payment = db.relationship('Payment', backref='booking', uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "seat_number": self.seat_number,
            "status": self.status,
            "booking_date": self.booking_date.isoformat(),
            "user_name": self.user.name if self.user else "Unknown",
            "matatu": {
                "id": self.matatu.id,
                "plate": self.matatu.plate_number, # Fixed from registration_number
                "route": self.matatu.route.origin + " - " + self.matatu.route.destination if self.matatu.route else "No Route"
            },
            "payment_status": self.payment.status if self.payment else "Unpaid"
        }