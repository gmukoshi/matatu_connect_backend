from app.models.user import User
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def backfill_drivers():
    with app.app_context():
        print("--- Backfilling Drivers ---")
        drivers = User.query.filter_by(role='driver').all()
        updated = 0
        for d in drivers:
            if d.sacco_id is None:
                print(f"Updating Driver {d.id} ({d.name}): Setting SaccoID=1, Status=approved")
                d.sacco_id = 1
                if not d.verification_status:
                    d.verification_status = "approved"
                updated += 1
        
        if updated > 0:
            db.session.commit()
            print(f"Successfully updated {updated} drivers.")
        else:
            print("No drivers needed backfilling.")
        print("--- Backfill Complete ---")

if __name__ == "__main__":
    backfill_drivers()
