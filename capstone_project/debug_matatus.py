from app.models.matatu import Matatu
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def debug_matatus():
    with app.app_context():
        print("--- Debugging Matatus ---")
        matatus = Matatu.query.all()
        print(f"Total matatus in database: {len(matatus)}")
        
        if matatus:
            for m in matatus:
                matatu_dict = m.to_dict()
                print(f"  - ID: {matatu_dict['id']}, Plate: {matatu_dict['plate_number']}, Driver: {matatu_dict['driver']}, Route: {matatu_dict['route']}")
        else:
            print("  No matatus found!")
        
        print("--- Debug Complete ---")

if __name__ == "__main__":
    debug_matatus()
