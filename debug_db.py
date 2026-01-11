import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from capstone_project.app import create_app, db
from capstone_project.app.models.user import User
from capstone_project.app.models.matatu import Matatu
from capstone_project.app.models.booking import Booking

app = create_app()

with app.app_context():
    print("=== USERS ===")
    for u in User.query.all():
        print(f"ID: {u.id}, Name: {u.name}, Role: {u.role}, Email: {u.email}")
    
    print("\n=== MATATUS ===")
    for m in Matatu.query.all():
        print(f"ID: {m.id}, Plate: {m.plate_number}, DriverID: {m.driver_id}, RouteID: {m.route_id}")

    print("\n=== BOOKINGS ===")
    for b in Booking.query.all():
        print(f"ID: {b.id}, MatatuID: {b.matatu_id}, Seat: {b.seat_number}, Status: {b.status}, UserID: {b.user_id}")
