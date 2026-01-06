from flask import request, Blueprint
from flask_restful import Resource, Api
from ..models.route import Route
from ..extensions import db
from ..utils.responses import make_response

# 1. This is the variable the error is looking for!
route_bp = Blueprint('route_bp', __name__)
api = Api(route_bp)

class RouteListResource(Resource):
    def get(self):
        try:
            routes = Route.query.all()
            return make_response(
                data=[r.to_dict() for r in routes], 
                message="Routes fetched successfully", 
                status_code=200
            )
        except Exception as e:
            return make_response(message="Error fetching routes", error=str(e), status_code=500)

# 2. Add the resources to the API within this file
api.add_resource(RouteListResource, '/routes')