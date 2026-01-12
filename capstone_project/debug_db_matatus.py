from app.models.matatu import Matatu
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def list_matatus():
    with app.app_context():
        print("--- Matatu Debug Start ---")
        matatus = Matatu.query.all()
        print(f"Total Matatus: {len(matatus)}")
        for m in matatus:
            print(f"ID: {m.id}, Plate: {m.plate_number}, Status: {m.assignment_status}, Driver: {m.driver_id}")
        print("--- Matatu Debug End ---")

if __name__ == "__main__":
    list_matatus()
