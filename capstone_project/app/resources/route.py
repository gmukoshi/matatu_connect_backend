from flask import request
from flask_restful import Resource
from ..models.route import Route
from ..extensions import db
from ..utils.responses import make_response

class RouteListResource(Resource):
    def get(self):
        try:
            routes = Route.query.all()
            data = [route.to_dict() for route in routes]
            return make_response(data=data, message="Routes fetched successfully", status=200)
        except Exception as e:
            return make_response(message="Error fetching routes", error=str(e), status=500)

    def post(self):
        data = request.get_json() or {}

        required = ("origin", "destination", "fare")
        if not all(k in data for k in required):
            return make_response(
                message="Validation Error",
                error="Missing fields: origin, destination, fare",
                status=400
            )

        existing_route = Route.query.filter_by(
            origin=data["origin"],
            destination=data["destination"]
        ).first()

        if existing_route:
            return make_response(message="Conflict", error="Route already exists", status=409)

        new_route = Route(
            origin=data["origin"],
            destination=data["destination"],
            fare=data["fare"],
            distance=data.get("distance"),
            estimated_duration=data.get("estimated_duration")
        )

        try:
            db.session.add(new_route)
            db.session.commit()
            return make_response(
                message="Route created successfully",
                data=new_route.to_dict(),
                status=201
            )
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)


class RouteResource(Resource):
    def get(self, route_id):
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Not found", error="Route not found", status=404)

        return make_response(message="Route fetched successfully", data=route.to_dict(), status=200)

    def patch(self, route_id):
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Not found", error="Route not found", status=404)

        body = request.get_json() or {}

        allowed_fields = {"origin", "destination", "fare", "distance", "estimated_duration"}
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if not updates:
            return make_response(
                message="Validation Error",
                error="No valid fields to update",
                status=400
            )

        for key, value in updates.items():
            setattr(route, key, value)

        try:
            db.session.commit()
            return make_response(message="Route updated successfully", data=route.to_dict(), status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)

    def delete(self, route_id):
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Not found", error="Route not found", status=404)

        try:
            db.session.delete(route)
            db.session.commit()
            return make_response(message="Route deleted successfully", status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)


def register_resources(api):
    api.add_resource(RouteListResource, "/routes")
    api.add_resource(RouteResource, "/routes/<int:route_id>")
