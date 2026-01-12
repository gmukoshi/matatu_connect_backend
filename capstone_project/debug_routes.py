from app.models.route import Route
from app.extensions import db
from app.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def debug_routes():
    with app.app_context():
        print("--- Debugging Routes ---")
        routes = Route.query.all()
        print(f"Total routes in database: {len(routes)}")
        
        if routes:
            for r in routes:
                route_dict = r.to_dict()
                print(f"  - ID: {route_dict['id']}, Route: {route_dict['name']}, Fare: KES {route_dict['fare']}")
        else:
            print("  No routes found in database!")
        
        print("\n--- Simulated API Response ---")
        from app.utils.responses import success_response
        response_data, status_code = success_response(data=[r.to_dict() for r in routes])
        print(f"Status Code: {status_code}")
        print(f"Response Structure: {response_data}")
        
        print("--- Debug Complete ---")

if __name__ == "__main__":
    debug_routes()
