from flask import request, Blueprint
from flask_restful import Resource, Api
from ..models.route import Route
from ..extensions import db
from ..utils.responses import success_response, error_response

route_bp = Blueprint('route_bp', __name__)
api = Api(route_bp)

class RouteListResource(Resource):
    def get(self):
        routes = Route.query.all()
        return success_response(data=[r.to_dict() for r in routes])

    def post(self):
        data = request.get_json()
        new_route = Route(
            origin=data['origin'],
            destination=data['destination'],
            fare=data['fare'],
            distance=data.get('distance'),
            estimated_duration=data.get('estimated_duration')
        )
        db.session.add(new_route)
        db.session.commit()
        return success_response(data=new_route.to_dict(), status_code=201)

api.add_resource(RouteListResource, '/')