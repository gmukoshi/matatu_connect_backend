from faker import Faker
from random import choice, randint

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.route import Route
from app.models.matatu import Matatu

fake = Faker()

def clear_data():
    # Clear in safe order based on FKs: Matatu depends on User
    db.session.query(Matatu).delete()
    db.session.query(Route).delete()
    db.session.query(User).delete()
    db.session.commit()

def seed_users(n=15):
    users = []

    # Create a few drivers so Matatu can reference them
    roles = (["driver"] * 6) + (["commuter"] * 8) + (["sacco_manager"] * 1)

    for _ in range(n):
        role = choice(roles)
        u = User(
            email=fake.unique.email(),
            role=role
        )
        u.set_password("Password123!")  # simple fixed password for dev
        users.append(u)

    db.session.add_all(users)
    db.session.commit()
    return users

def seed_routes(n=10):
    routes = []
    for _ in range(n):
        origin = fake.city()
        destination = fake.city()

        r = Route(
            origin=origin,
            destination=destination,
            fare=float(randint(50, 400)),              # KES
            distance=float(randint(2, 40)),            # km
            estimated_duration=f"{randint(10, 120)} minutes"
        )
        routes.append(r)

    db.session.add_all(routes)
    db.session.commit()
    return routes

def seed_matatus(users, n=12):
    drivers = [u for u in users if u.role == "driver"]

    # If no drivers exist for some reason, fall back to any users
    pool = drivers if drivers else users

    matatus = []
    for _ in range(n):
        m = Matatu(
            plate_number=fake.unique.bothify(text="K?? ###?"),
            capacity=randint(10, 33),
            driver_id=choice(pool).id
        )
        matatus.append(m)

    db.session.add_all(matatus)
    db.session.commit()
    return matatus

def run_seed():
    clear_data()
    users = seed_users(15)
    seed_routes(10)
    seed_matatus(users, 12)
    print("Seed complete: users, routes, matatus created.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_seed()
