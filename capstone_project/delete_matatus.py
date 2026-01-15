from app import create_app
from app.extensions import db
from app.models.matatu import Matatu
from sqlalchemy import text

app = create_app()

def delete_all_matatus():
    with app.app_context():
        print("🗑️ Deleting all Matatus...")
        try:
            num_deleted = db.session.query(Matatu).delete()
            db.session.commit()
            print(f"✅ Successfully deleted {num_deleted} matatus.")
            
            # Optional: Reset sequence if using Postgres
            try:
                db.session.execute(text("ALTER SEQUENCE matatus_id_seq RESTART WITH 1;"))
                db.session.commit()
                print("🔄 Sequence reset.")
            except Exception as e:
                print(f"⚠️ Could not reset sequence (might not be Postgres or permission issue): {e}")

        except Exception as e:
            print(f"❌ Error deleting matatus: {e}")
            db.session.rollback()

if __name__ == "__main__":
    delete_all_matatus()
