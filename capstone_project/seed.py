from faker import Faker
from random import choice, randint

from flask import Flask
from app.config import DevelopmentConfig
from app.extensions import db

from app.models.user import User
from app.models.matatu import Matatu

fake = Faker()

def make_seed_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    return app

def clear_data():
    # Matatu depends on User
    db.session.query(Matatu).delete()
    db.session.query(User).delete()
    db.session.commit()

def seed_users(n=15):
    users = []
    roles = (["driver"] * 6) + (["commuter"] * 8) + (["sacco_manager"] * 1)

    for _ in range(n):
        u = User(email=fake.unique.email(), role=choice(roles))
        u.set_password("Password123!")
        users.append(u)

    db.session.add_all(users)
    db.session.commit()
    return users

def seed_matatus(users, n=12):
    drivers = [u for u in users if u.role == "driver"]
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
def ensure_tables():
    db.create_all()

def run_seed():
    clear_data()
    users = seed_users(15)
    seed_matatus(users, 12)
    print("Seed complete: users and matatus created.")

if __name__ == "__main__":
    app = make_seed_app()
    with app.app_context():
        ensure_tables()
        run_seed()
