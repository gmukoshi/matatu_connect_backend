from app import create_app
from app.extensions import db
from app.models.log import MatatuLog

app = create_app()

def create_tables():
    with app.app_context():
        print("Creating missing tables...")
        # This will create tables for models that are imported and registered but missing in DB
        db.create_all()
        print("Tables created.")

if __name__ == "__main__":
    create_tables()
