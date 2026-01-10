from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    # Role Constants
    ROLE_COMMUTER = "commuter"
    ROLE_DRIVER = "driver"
    ROLE_SACCO_MANAGER = "sacco_manager"
    ROLE_ADMIN = "admin"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Added for better UI personalized greeting
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(50),
        nullable=False,
        default=ROLE_COMMUTER
    )
    # Link drivers/managers to a Sacco
    sacco_id = db.Column(db.Integer, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Helper to return user data for JWT identity or API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "sacco_id": self.sacco_id
        }