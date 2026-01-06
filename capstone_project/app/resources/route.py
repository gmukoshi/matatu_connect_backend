from flask import request, Blueprint
from flask_restful import Resource, Api
from ..models.route import Route
from ..extensions import db
from ..utils.responses import make_response

# 1. Define the Blueprint and the API object
route_bp = Blueprint('route_bp', __name__)
api = Api(route_bp)

class RouteListResource(Resource):
    def get(self):
        """Fetch all available transit routes"""
        try:
            routes = Route.query.all()
            data = [r.to_dict() for r in routes]
            return make_response(
                data=data, 
                message="Routes fetched successfully", 
                status_code=200
            )
        except Exception as e:
            return make_response(message="Error fetching routes", error=str(e), status_code=500)

    def post(self):
        """Create a new route (e.g., Nairobi to Thika)"""
        data = request.get_json() or {}
        
        # Validation
        if not data.get("name") or not data.get("destination"):
            return make_response(
                message="Validation Error", 
                error="Name and destination are required", 
                status_code=400
            )

        new_route = Route(
            name=data["name"],
            origin=data.get("origin", "CBD"), # Default to CBD if not provided
            destination=data["destination"],
            base_fare=data.get("base_fare", 0.0)
        )
        
        try:
            db.session.add(new_route)
            db.session.commit()
            return make_response(
                message="Route created successfully", 
                data=new_route.to_dict(), 
                status_code=201
            )
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database error", error=str(e), status_code=500)

class RouteResource(Resource):
    def get(self, route_id):
        """Get details for a specific route"""
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Route not found", status_code=404)
        return make_response(data=route.to_dict(), status_code=200)

    def patch(self, route_id):
        """Update route details like fare or destination name"""
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Route not found", status_code=404)

        data = request.get_json() or {}
        
        # Update allowed fields
        for field in ['name', 'origin', 'destination', 'base_fare']:
            if field in data:
                setattr(route, field, data[field])
        
        try:
            db.session.commit()
            return make_response(
                message="Route updated successfully", 
                data=route.to_dict(), 
                status_code=200
            )
        except Exception as e:
            db.session.rollback()
            return make_response(message="Update failed", error=str(e), status_code=500)

    def delete(self, route_id):
        """Remove a route from the system"""
        route = Route.query.get(route_id)
        if not route:
            return make_response(message="Route not found", status_code=404)

        try:
            db.session.delete(route)
            db.session.commit()
            return make_response(message="Route deleted successfully", status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Deletion failed", error=str(e), status_code=500)

# 2. Map the resources to specific URLs
# Note: These paths are relative to the blueprint prefix (/api/routes)
api.add_resource(RouteListResource, '/')
api.add_resource(RouteResource, '/<int:route_id>')