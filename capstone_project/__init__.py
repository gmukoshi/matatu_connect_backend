from flask import Flask
from .app.extensions import db, migrate, jwt, mail, socketio
from .app import realtime
from .app.config import DevelopmentConfig
from flask_restful import Api
from .app.resources.route import register_resources

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    api=Api(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    from .app.models import route, matatu

    from .app.resources.route import register_resources
    register_resources(api)

    return app
