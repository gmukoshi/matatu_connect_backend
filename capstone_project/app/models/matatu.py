from datetime import datetime
from app.extensions import db

class Matatu(db.Model):
    __tablename__ = "matatus"

    id = db.Column(db.Integer, primary_key=True)
    sacco_id = db.Column(db.Integer, nullable=False, index=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=True, index=True)

    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignment_status = db.Column(db.String(20), default="pending") # pending, active, rejected

    # Relationships
    driver = db.relationship("User", backref=db.backref("matatus", lazy=True))
    route = db.relationship("Route", backref=db.backref("matatus", lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        route_data = None
        if self.route:
            route_dict = self.route.to_dict()
            route_data = {
                "id": route_dict["id"],
                "name": route_dict["name"],  # This is computed in Route.to_dict()
                "origin": route_dict["origin"],
                "destination": route_dict["destination"]
            }
        
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "capacity": self.capacity,
            "driver_id": self.driver_id,
            "driver": self.driver.name if self.driver else "No Driver Assigned",
            "assignment_status": self.assignment_status,
            "route_id": self.route_id,
            "route": route_data,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }