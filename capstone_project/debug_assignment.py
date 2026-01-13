
from app import create_app, db
from app.models.matatu import Matatu
from app.models.user import User

app = create_app()

with app.app_context():
    print("--- MATATU DRIVER ASSIGNMENTS ---")
    matatus = Matatu.query.all()
    for m in matatus:
        driver_name = m.driver.name if m.driver else "UNASSIGNED"
        driver_email = m.driver.email if m.driver else "N/A"
        print(f"Matatu: {m.plate_number} (ID: {m.id}) -> Driver: {driver_name} (ID: {m.driver_id}) Email: {driver_email}")

    print("\n--- AVAILABLE DRIVERS ---")
    drivers = User.query.filter_by(role='driver').all()
    for d in drivers:
        assigned_matatu = Matatu.query.filter_by(driver_id=d.id).first()
        status = f"Assigned to {assigned_matatu.plate_number}" if assigned_matatu else "UNASSIGNED"
        print(f"ID: {d.id} | {d.name} | {d.email} | {status}")
