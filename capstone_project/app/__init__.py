import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt, migrate, socketio
from .utils.errors import (
    handle_404_error, 
    handle_500_error, 
    handle_403_error, 
    handle_401_error
)

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 1. Database URL Fix for Render
    # Render provides 'postgres://', but SQLAlchemy 1.4+ needs 'postgresql://'
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # 2. Configurations
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-key-for-local-only"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "jwt-dev-key")
    )

    # 3. CORS - Allow your deployed frontend and local dev
    # Add your actual Render frontend URL to this list once deployed
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5555"
        "https://your-frontend-name.onrender.com" 
    ]
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

    # 4. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*") # Required for WebSockets to work across domains

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

    # 7. Socket Events
    with app.app_context():
        from app.sockets import events

    @app.route('/')
    def health_check():
        return {"status": "success", "message": "Matatu Connect API Operational"}, 200

    return app