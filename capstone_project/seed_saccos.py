from app import create_app, db
from app.models.sacco import Sacco
from sqlalchemy import text

app = create_app()

def seed_saccos():
    with app.app_context():
        # 1. Sync Sequence
        print("Syncing Sacco ID sequence...")
        try:
            db.session.execute(text("SELECT setval('saccos_id_seq', (SELECT MAX(id) FROM saccos));"))
            db.session.commit()
        except Exception as e:
            print(f"Sequence sync warning (might be empty table): {e}")
            db.session.rollback()

        # 2. Seed
        saccos_to_add = [
            "2NK Sacco",
            "Super Metro",
            "Prestige Sacco",
            "Kakamega Sacco",
            "Mololine Sacco",
            "Easy Coach",
            "North Rift Shuttle",
            "Classic Shuttle",
            "Nairobi City Sacco"
        ]

        print("--- Seeding Saccos ---")
        added_count = 0
        
        for name in saccos_to_add:
            existing = Sacco.query.filter_by(name=name).first()
            if not existing:
                new_sacco = Sacco(name=name)
                db.session.add(new_sacco)
                added_count += 1
                try:
                    db.session.commit()
                    print(f"Created: {name}")
                except Exception as e:
                    print(f"Error creating {name}: {e}")
                    db.session.rollback()
            else:
                print(f"Skipped (Exists): {name}")
        
        print("Seeding Done.")

if __name__ == "__main__":
    seed_saccos()
