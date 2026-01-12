from app.models.user import User
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def inspect_drivers():
    with app.app_context():
        print("--- Driver Inspection Start ---")
        drivers = User.query.filter_by(role='driver').all()
        print(f"Total Drivers Found: {len(drivers)}")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'SaccoID':<10} {'Status':<10}")
        print("-" * 80)
        for d in drivers:
            status = d.verification_status or "None"
            name = d.name or "Unknown"
            sacco = str(d.sacco_id) if d.sacco_id is not None else "None"
            print(f"{d.id:<5} {name:<20} {d.email:<30} {sacco:<10} {status:<10}")
        print("--- Driver Inspection End ---")

if __name__ == "__main__":
    inspect_drivers()
