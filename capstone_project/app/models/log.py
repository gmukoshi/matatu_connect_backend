from datetime import datetime
from app.extensions import db

class MatatuLog(db.Model):
    __tablename__ = "matatu_logs"

    id = db.Column(db.Integer, primary_key=True)
    
    matatu_id = db.Column(db.Integer, db.ForeignKey("matatus.id"), nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    log_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    
    passengers_carried = db.Column(db.Integer, default=0, nullable=False)
    fuel_liters = db.Column(db.Float, default=0.0, nullable=False)
    mileage_km = db.Column(db.Float, default=0.0, nullable=False)
    
    amount_spent = db.Column(db.Float, default=0.0) # Cost of fuel/expenses
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    matatu = db.relationship("Matatu", backref=db.backref("logs", lazy=True))
    driver = db.relationship("User", backref=db.backref("logs", lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "matatu_id": self.matatu_id,
            "driver_name": self.driver.name if self.driver else "Unknown",
            "log_date": self.log_date.isoformat(),
            "passengers": self.passengers_carried,
            "fuel_liters": self.fuel_liters,
            "mileage_km": self.mileage_km,
            "created_at": self.created_at.isoformat()
        }
