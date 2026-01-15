import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, jwt, migrate, socketio
from .utils.errors import (
    handle_404_error, 
    handle_500_error, 
    handle_403_error, 
    handle_401_error
)

load_dotenv()

def create_app(config_class=None):
    # Calculate path to frontend dist folder
    # Assuming structure:
    # backend/capstone_project/app/__init__.py
    # frontend/dist
    basedir = os.path.abspath(os.path.dirname(__file__)) # .../app
    backend_root = os.path.dirname(os.path.dirname(basedir)) # .../matatu_connect_backend
    frontend_dist = os.path.join(os.path.dirname(backend_root), 'matatu_connect_frontend', 'dist')

    app = Flask(__name__, static_folder=frontend_dist, static_url_path='/')
    
    # Configure JSON Logging
    import logging
    import json
    from flask import request
    
    # Disable default Werkzeug logging (Standard Access Logs)
    werkzeug_log = logging.getLogger('werkzeug')
    werkzeug_log.setLevel(logging.ERROR) # Only log errors from werkzeug
    werkzeug_log.disabled = True # Try completely disabling if setLevel isn't enough for dev server

    @app.after_request
    def log_request_info(response):
        # Only log API requests to keep terminal clean ('api is being consumed')
        if request.path.startswith('/api'):
            log_data = {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "ip": request.remote_addr,
            }
            # Use app.logger to output the JSON
            # We use print directly if app.logger formats it with extra text, 
            # but app.logger is standard. Let's stick to app.logger but maybe format it content-only if needed.
            # Using print + flush to ensure it's raw JSON line if that's what they strictly want
            print(json.dumps(log_data), flush=True) 
            
        return response
    
    # Load configuration
    if config_class is None:
        # Default to DevelopmentConfig
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        
        # Override with any manual environment updates if needed (e.g. Render DB fix)
        database_url = os.getenv("DATABASE_URL")
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Load the provided config class (e.g. TestingConfig)
        app.config.from_object(config_class)

    # 3. CORS - Allow your deployed frontend and local dev
    # Add your actual Render frontend URL to this list once deployed
    # 3. CORS - Allow your deployed frontend and any localhost port for dev
    # Add your actual Render frontend URL to this list once deployed
    allowed_origins = [
        os.getenv("FRONTEND_URL"),
        "https://matatu-connect-frontend.vercel.app",
        r"https://.*\.vercel\.app", # Allow ANY Vercel deployment (preview/prod)
        r"https?://localhost:\d+",
        r"https?://127\.0\.0\.1:\d+"
    ]
    # Filter out None values
    allowed_origins = [origin for origin in allowed_origins if origin]
    
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

    # 4. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*") # Required for WebSockets to work across domains

    # JWT Error handlers for debugging
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"DEBUG: JWT Invalid Token: {error_string}")
        return jsonify({"message": "Invalid Token", "error": error_string}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"DEBUG: JWT Expired:Header={jwt_header} Payload={jwt_payload}")
        return jsonify({"message": "Token Expired", "error": "token_expired"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        print(f"DEBUG: JWT Missing: {error_string}")
        return jsonify({"message": "Missing Token", "error": error_string}), 401

    # 5. Error Handlers
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(401, handle_401_error)

    # 6. Blueprints
    from app.resources.auth import auth_bp
    from app.resources.user import user_bp
    from app.resources.matatu import matatu_bp
    from app.resources.route import route_bp
    from app.resources.dashboard import dashboard_bp
    from app.resources.booking import booking_bp
    from app.resources.payment import payment_bp 

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(matatu_bp, url_prefix='/api/matatus')
    app.register_blueprint(route_bp, url_prefix='/api/routes')
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    from app.resources.rating import rating_bp
    from app.resources.log import log_bp

    app.register_blueprint(rating_bp, url_prefix="/api/ratings")
    app.register_blueprint(log_bp, url_prefix="/api/logs")
    
    from app.resources.notification import notification_bp
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")
    
    from app.resources.sacco import sacco_bp
    app.register_blueprint(sacco_bp, url_prefix="/api/saccos")

    # 7. Socket Events
    with app.app_context():
        from app.sockets import events

    @app.route('/')
    def serve_frontend():
        return app.send_static_file('index.html')

    @app.route('/health')
    def health_check():
        return {"status": "success", "message": "Matatu Connect API Operational"}, 200

    # Catch-all for React routing (explicit fallback for 404s handled in errors.py, 
    # but this handles direct deep links if server supports it, though usually 404 handler is key)

    return app