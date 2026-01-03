from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, jwt, mail, socketio
from .config import DevelopmentConfig
from .utils.errors import (
    handle_404_error,
    handle_500_error,
    handle_403_error,
    handle_401_error
)
   
def create_app():
    app = Flask(__name__)

    # 1. Load Configurations (Database URI, Secret Keys, etc.)
    # import path
    app.config.from_object('app.config.DevelopmentConfig')

    # 2. Integrate CORS
    # Allows React frontend to access the API
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True
    )

    # 3. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)

    # 4. Register Global Error Handlers
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(401, handle_401_error)

    # 5. Register Blueprints
    from .resources.auth import auth_bp 
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Future blueprints
    # from app.resources.matatu import matatu_bp
    # app.register_blueprint(matatu_bp, url_prefix='/api/matatus')
#--------------------------------------



    #from .resources import register_resources
    #register_resources(app)

    #return app
