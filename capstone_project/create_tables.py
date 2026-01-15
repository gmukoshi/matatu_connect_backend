from app import create_app
from app.extensions import db
from app.models.log import MatatuLog
from app.models.user import User
from app.models.matatu import Matatu
from app.models.route import Route
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.sacco import Sacco
from app.models.rating import Rating

app = create_app()

def create_tables():
    with app.app_context():
        print("Creating missing tables...")
        # This will create tables for models that are imported and registered but missing in DB
        db.create_all()
        print("Tables created.")

if __name__ == "__main__":
    create_tables()
