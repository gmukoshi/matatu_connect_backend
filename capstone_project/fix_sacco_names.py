from app import create_app, db
from app.models.sacco import Sacco
from app.models.user import User
from app.models.matatu import Matatu

app = create_app()

def fix_sacco_names():
    with app.app_context():
        print("--- Migrating Usage from 'Matatu Connect Sacco' to '2NK Sacco' ---")
        
        # 1. Get the Saccos
        old_sacco = Sacco.query.filter_by(name="Matatu Connect Sacco").first()
        target_sacco = Sacco.query.filter_by(name="2NK Sacco").first()
        
        if not old_sacco:
            print("Old 'Matatu Connect Sacco' not found. Nothing to do.")
            return

        if not target_sacco:
            print("Target '2NK Sacco' not found. Creating it...")
            target_sacco = Sacco(name="2NK Sacco")
            db.session.add(target_sacco)
            db.session.commit()
            print(f"Created 2NK Sacco with ID: {target_sacco.id}")

        print(f"Migrating data from ID {old_sacco.id} to ID {target_sacco.id}...")

        # 2. Reassign Users (Managers & Drivers)
        users = User.query.filter_by(sacco_id=old_sacco.id).all()
        for u in users:
            u.sacco_id = target_sacco.id
        print(f"Reassigned {len(users)} users.")

        # 3. Reassign Matatus
        matatus = Matatu.query.filter_by(sacco_id=old_sacco.id).all()
        for m in matatus:
            m.sacco_id = target_sacco.id
        print(f"Reassigned {len(matatus)} matatus.")

        # 4. Delete Old Sacco
        db.session.delete(old_sacco)
        db.session.commit()
        
        print("--- Migration Complete. 'Matatu Connect Sacco' deleted. ---")

if __name__ == "__main__":
    fix_sacco_names()
