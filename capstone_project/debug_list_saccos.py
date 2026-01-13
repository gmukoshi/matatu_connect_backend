from app import create_app, db
from app.models.sacco import Sacco

app = create_app()

def list_saccos():
    with app.app_context():
        saccos = Sacco.query.all()
        print(f"Total Saccos: {len(saccos)}")
        for s in saccos:
            print(f"ID: {s.id}, Name: {s.name}")

if __name__ == "__main__":
    list_saccos()
