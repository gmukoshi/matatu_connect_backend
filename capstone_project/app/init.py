from flask import Flask
from .extensions import db, migrate, jwt, mail, socketio
from .config import DevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    from .resources import register_resources
    register_resources(app)

    return app
