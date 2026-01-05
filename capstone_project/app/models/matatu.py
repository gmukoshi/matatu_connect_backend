from datetime import datetime
from app.extensions import db


class Matatu(db.Model):
    __tablename__ = "matatus"

    id = db.Column(db.Integer, primary_key=True)

    sacco_id = db.Column(db.Integer, nullable=False, index=True)

    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    route_id = db.Column(
        db.Integer,
        db.ForeignKey("routes.id"),
        nullable=True,
        index=True
    )

    # 🔴 Live GPS Tracking
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    last_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ------------------
    # Relationships
    # ------------------
    driver = db.relationship("User", backref="matatus")
    route = db.relationship("Route", backref="matatus")

    # ------------------
    # Helpers
    # ------------------
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "capacity": self.capacity,
            "driver_id": self.driver_id,
            "route_id": self.route_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "last_updated": (
                self.last_updated.isoformat()
                if self.last_updated else None
            )
        }
