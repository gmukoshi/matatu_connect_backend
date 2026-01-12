from app.models.user import User
from app.models.sacco import Sacco
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def assign_manager_sacco():
    with app.app_context():
        # Create Sacco table if not exists (quick hack since no migration setup)
        db.create_all() 
        
        print("--- Assigning Manager Sacco ---")
        # 1. Create Default Sacco
        sacco_name = "Matatu Connect Sacco"
        sacco = Sacco.query.filter_by(name=sacco_name).first()
        if not sacco:
            print(f"Creating Sacco: {sacco_name}")
            sacco = Sacco(name=sacco_name)
            sacco.id = 1 # Force ID 1 to match our driver backfill
            db.session.add(sacco)
            db.session.commit()
        else:
            print(f"Sacco found: {sacco.name} (ID: {sacco.id})")
            
        # 2. Assign Managers
        managers = User.query.filter_by(role='sacco_manager').all()
        updated = 0
        for m in managers:
            if not m.sacco_id:
                print(f"Assigning Manager {m.name} ({m.email}) to Sacco {sacco.id}")
                m.sacco_id = sacco.id
                updated += 1
        
        if updated > 0:
            db.session.commit()
            print(f"Successfully updated {updated} managers.")
        else:
            print("No managers needed assignment.")
            
        print("--- Assignment Complete ---")

if __name__ == "__main__":
    assign_manager_sacco()
