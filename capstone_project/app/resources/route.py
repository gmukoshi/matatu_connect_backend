from flask import request
from flask_restful import Resource
from app.models.route import Route
from app.extensions import db
from app.utils.responses import make_response # Import the helper

class RouteListResource(Resource):
    def get(self):
        """Get all available routes"""
        try:
            routes = Route.query.all()
            data = [route.to_dict() for route in routes]
            return make_response(data=data, message="Routes fetched successfully", status=200)
        except Exception as e:
            return make_response(message="Error fetching routes", error=str(e), status=500)

    def post(self):
        """Create a new route"""
        data = request.get_json()

        if not data or not all(k in data for k in ('origin', 'destination', 'fare')):
            return make_response(message="Validation Error", error="Missing fields: origin, destination, fare", status=400)

        existing_route = Route.query.filter_by(origin=data['origin'], destination=data['destination']).first()
        if existing_route:
            return make_response(message="Conflict", error="Route already exists", status=409)

        new_route = Route(
            origin=data['origin'],
            destination=data['destination'],
            fare=data['fare'],
            distance=data.get('distance'),
            estimated_duration=data.get('estimated_duration')
        )

        try:
            new_route.save()
            return make_response(
                message="Route created successfully", 
                data=new_route.to_dict(), 
                status=201
            )
        except Exception as e:
            return make_response(message="Database Error", error=str(e), status=500)