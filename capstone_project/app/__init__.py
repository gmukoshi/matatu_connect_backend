from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .extensions import db, migrate, jwt, mail, socketio
from .config import DevelopmentConfig
from .utils.errors import (
    handle_404_error,
    handle_500_error,
    handle_403_error,
    handle_401_error,
)


def create_app():
    app = Flask(__name__)

    # 1) Load config
    app.config.from_object(DevelopmentConfig)

    # 2) CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )

    # 3) Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)

    # 4) Error handlers
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(401, handle_401_error)

    # 5) Register API resources
    api = Api(app)
    from .resources import register_resources
    register_resources(app, api)

    # 6) Register blueprints (if you still use blueprints)
    from .resources.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    from app.resources.route import register_resources
    register_resources(api)

    return app
