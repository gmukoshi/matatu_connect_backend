from faker import Faker
from random import choice, randint
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.matatu import Matatu
from app.models.route import Route

fake = Faker()

def clear_data():
    print("Clearing old data...")
    # Delete in order of dependency
    db.session.query(Matatu).delete()
    db.session.query(Route).delete()
    db.session.query(User).delete()
    db.session.commit()

def seed_users(n=15):
    print(f"Seeding {n} users...")
    users = []
    roles = (["driver"] * 6) + (["commuter"] * 8) + (["sacco_manager"] * 1)
    
    for _ in range(n):
        u = User(
            name=fake.name(),
            email=fake.unique.email(), 
            role=choice(roles)
        )
        u.set_password("Password123!")
        users.append(u)
    
    db.session.add_all(users)
    db.session.commit()
    return users

def seed_routes():
    print("Seeding routes...")
    route_data = [
        {"origin": "Nairobi CBD", "destination": "Ngong", "fare": 100, "distance": 22},
        {"origin": "Nairobi CBD", "destination": "Kikuyu", "fare": 80, "distance": 20},
        {"origin": "Nairobi CBD", "destination": "Thika", "fare": 120, "distance": 42},
        {"origin": "Nairobi CBD", "destination": "Kitengela", "fare": 150, "distance": 30},
    ]
    
    routes = []
    for data in route_data:
        r = Route(
            origin=data["origin"],
            destination=data["destination"],
            fare=data["fare"],
            distance=data["distance"],
            estimated_duration=f"{randint(45, 90)} mins"
        )
        routes.append(r)
    
    db.session.add_all(routes)
    db.session.commit()
    return routes

def seed_matatus(users, routes, n=12):
    print(f"Seeding {n} matatus...")
    drivers = [u for u in users if u.role == "driver"]
    
    matatus = []
    for _ in range(n):
        m = Matatu(
            plate_number=fake.unique.bothify(text="K?? ###?").upper(),
            capacity=choice([14, 29, 33]),
            sacco_id=randint(1, 5),
            driver_id=choice(drivers).id if drivers else None,
            route_id=choice(routes).id if routes else None,
            # Random starting coordinates for Nairobi area
            latitude=-1.286389 + (randint(-100, 100) / 1000),
            longitude=36.817223 + (randint(-100, 100) / 1000)
        )
        matatus.append(m)

    db.session.add_all(matatus)
    db.session.commit()
    print("✅ Seed complete!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # This ensures tables are created even if migrations haven't run
        db.create_all()
        
        try:
            clear_data()
            users = seed_users(20)
            routes = seed_routes()
            seed_matatus(users, routes, 12)
        except Exception as e:
            print(f"❌ Error during seed: {e}")
            db.session.rollback()