from .auth import auth_bp
from .route import RouteListResource

def register_resources(app, api):
    # Blueprint routes
    app.register_blueprint(auth_bp)

    # Flask-RESTful resources
    api.add_resource(RouteListResource, "/routes")
