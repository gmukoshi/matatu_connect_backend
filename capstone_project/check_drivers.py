from app.models.user import User
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def check_data():
    with app.app_context():
        print("--- Checking Users ---")
        managers = User.query.filter_by(role='sacco_manager').all()
        print(f"Managers ({len(managers)}):")
        for m in managers:
            print(f"  - ID: {m.id}, Name: {m.name}, SaccoID: {m.sacco_id}, Email: {m.email}")

        drivers = User.query.filter_by(role='driver').all()
        print(f"\nDrivers ({len(drivers)}):")
        for d in drivers:
            print(f"  - ID: {d.id}, Name: {d.name}, SaccoID: {d.sacco_id}, Status: {d.verification_status}, Email: {d.email}")
            
if __name__ == "__main__":
    check_data()
