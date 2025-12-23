from app.extensions import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False)      # Start Point
    destination = db.Column(db.String(100), nullable=False) # End Point
    fare = db.Column(db.Float, nullable=False)              # Price (KES)
    distance = db.Column(db.Float, nullable=True)           # Distance in KM (Optional)
    estimated_duration = db.Column(db.String(50), nullable=True) # e.g., "2 hours"
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # A route can have many Matatus assigned to it
    matatus = db.relationship('Matatu', backref='route', lazy=True)
    # A route has many Bookings
    bookings = db.relationship('Booking', backref='route', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'fare': self.fare,
            'distance': self.distance,
            'estimated_duration': self.estimated_duration,
            'name': f"{self.origin} - {self.destination}" # Helper for UI display
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()