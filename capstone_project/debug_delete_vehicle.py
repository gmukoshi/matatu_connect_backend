from app.models.matatu import Matatu
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def try_delete():
    with app.app_context():
        print("--- Trying to Delete Vehicle ---")
        # Find a vehicle to delete (preferably one created recently or failing)
        # Check if any vehicle exists first
        vehicle = Matatu.query.first()
        if not vehicle:
            print("No vehicles found to delete.")
            return

        print(f"Attempting to delete Vehicle ID: {vehicle.id}, Plate: {vehicle.plate_number}")
        try:
            db.session.delete(vehicle)
            db.session.commit()
            print("Successfully deleted vehicle.")
        except Exception as e:
            print(f"FAILED to delete vehicle. Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    try_delete()
