import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt, migrate, socketio
from .utils.errors import (
    handle_404_error, 
    handle_500_error, 
    handle_403_error, 
    handle_401_error
)

def create_app():
    """
    Application Factory Pattern: This function initializes the Flask app,
    extensions, and registers all blueprints.
    """
    app = Flask(__name__)
    
    # 1. Load Configurations
    # Connects to PostgreSQL/SQLite and sets JWT secret keys
    from app.config import Config
    app.config.from_object(Config)

    # 2. Integrate CORS
    # Crucial for your React frontend (port 5173) to communicate with this API
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # 3. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # 4. Register Global Error Handlers
    # Provides clean JSON error messages to your React frontend
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(401, handle_401_error)

    # 5. Blueprint Registration (The Logic Layer)
    # We import these INSIDE the function to prevent 'Circular Import' errors
    with app.app_context():
        from app.resources.auth import auth_bp
        from app.resources.user import user_bp
        from app.resources.matatu import matatu_bp
        from app.resources.route import route_bp
        from app.resources.dashboard import dashboard_bp
        from app.resources.booking import booking_bp
        # Added payment_bp for the M-Pesa integration
        from app.resources.payment import payment_bp 

        # Auth & Users
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(user_bp, url_prefix='/api/users')
        
        # Core Transit Logic
        app.register_blueprint(matatu_bp, url_prefix='/api/matatus')
        app.register_blueprint(route_bp, url_prefix='/api/routes')
        
        # Fintech & Bookings
        app.register_blueprint(booking_bp, url_prefix="/api/bookings")
        app.register_blueprint(payment_bp, url_prefix="/api/payments")
        
        # Analytics & Overview
        app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

        # 6. Real-time Events
        # This handles the live matatu movement on your map
        from app.sockets import events

    # Simple health check route
    @app.route('/')
    def health_check():
        return {
            "status": "success", 
            "message": "Matatu Connect API is fully operational",
            "version": "1.0.0"
        }, 200

    return app