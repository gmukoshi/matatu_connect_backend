import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt, migrate,socketio
from .utils.errors import (
    handle_404_error, 
    handle_500_error, 
    handle_403_error, 
    handle_401_error
)

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)
    
    # 1. Load Configurations from app/config.py
    # This connects your PostgreSQL database and JWT keys
    from app.config import Config # Import the base Config class directly
    app.config.from_object(Config)

    # 2. Integrate CORS
    # Link: Allows your React frontend (port 5173) to access this API
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # 3. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # 4. Register Global Error Handlers
    # This ensures that if the backend crashes, the frontend gets a clean JSON message
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(401, handle_401_error)

    # 5. Register Blueprints (Routes)
    from app.resources.auth import auth_bp
    from app.resources.user import user_bp
    from app.resources.matatu import matatu_bp
    from app.resources.route import route_bp
    from app.resources.dashboard import dashboard_bp
    from app.resources.booking import booking_bp

    # All auth routes will now start with /api/auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(matatu_bp, url_prefix='/api/matatus')
    app.register_blueprint(route_bp, url_prefix='/api/routes')
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")

     # Register socket events
    from app.sockets import events

    # Simple health check route
    @app.route('/')
    def health_check():
        return {"status": "success", "message": "Matatu Connect API is running"}, 200

    return app