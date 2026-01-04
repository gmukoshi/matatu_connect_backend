from .auth import auth_bp
from .route import RouteListResource
from .user import UserListResource, UserResource, RegisterResource

def register_user_resources(api):
    api.add_resource(RegisterResource, "/auth/register")
    api.add_resource(UserListResource, "/users")                 # optional admin
    api.add_resource(UserResource, "/users/<int:user_id>")       # optional

def register_resources(app, api):
    # Blueprint routes
    app.register_blueprint(auth_bp)

    # Flask-RESTful resources
    api.add_resource(RouteListResource, "/routes")
