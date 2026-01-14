from app import create_app, db
from app.models.user import User
from app.models.matatu import Matatu

app = create_app()
with app.app_context():
    email = "driver26@trial.com"
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"Driver {email} not found")
    else:
        print(f"Driver: {user.name} (ID: {user.id}) | Sacco: {user.sacco_id}")
        vehicles = Matatu.query.filter_by(driver_id=user.id).all()
        for v in vehicles:
            print(f"  > Vehicle: {v.plate_number} (ID: {v.id}) | Status: {v.assignment_status}")
