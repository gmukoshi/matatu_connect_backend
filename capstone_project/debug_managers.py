
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("--- SACCO MANAGERS ---")
    managers = User.query.filter_by(role='sacco_manager').all()
    if not managers:
        print("No Sacco Managers found.")
    
    for m in managers:
        print(f"ID: {m.id} | Name: {m.name} | Email: {m.email} | Sacco ID: {m.sacco_id}")

    print("\n--- MATATUS ---")
    from app.models.matatu import Matatu
    matatus = Matatu.query.all()
    for m in matatus:
         print(f"Matatu ID: {m.id} | Plate: {m.plate_number} | Sacco ID: {m.sacco_id}")
