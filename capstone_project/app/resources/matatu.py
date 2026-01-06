from flask import request, Blueprint
from flask_restful import Resource, Api

from ..models.matatu import Matatu
from ..extensions import db
from ..utils.responses import make_response

# 1. Define the Blueprint and API object
matatu_bp = Blueprint('matatu_bp', __name__)
api = Api(matatu_bp)

class MatatuListResource(Resource):
    def get(self):
        """Fetch all matatus from the database"""
        try:
            matatus = Matatu.query.all()
            data = [m.to_dict() for m in matatus]
            return make_response(
                data=data, 
                message="Matatus fetched successfully", 
                status_code=200
            )
        except Exception as e:
            return make_response(
                message="Error fetching matatus", 
                error=str(e), 
                status_code=500
            )

    def post(self):
        """Register a new matatu to the fleet"""
        data = request.get_json() or {}

        # Validation: Plate number is mandatory
        if not data.get("plate_number"):
            return make_response(
                message="Validation Error",
                error="Missing required field: plate_number",
                status_code=400,
            )

        new_matatu = Matatu(
            plate_number=data["plate_number"],
            capacity=data.get("capacity", 14), # Default to 14 seater if not specified
            route_id=data.get("route_id"),
        )

        try:
            db.session.add(new_matatu)
            db.session.commit()
            return make_response(
                message="Matatu registered successfully",
                data=new_matatu.to_dict(),
                status_code=201,
            )
        except Exception as e:
            db.session.rollback()
            return make_response(
                message="Database Error", 
                error=str(e), 
                status_code=500
            )

class MatatuResource(Resource):
    def get(self, matatu_id):
        """Fetch a single matatu by ID"""
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status_code=404)
        return make_response(data=matatu.to_dict(), status_code=200)

    def patch(self, matatu_id):
        """Update matatu details (e.g., change route or capacity)"""
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status_code=404)

        body = request.get_json() or {}
        allowed_fields = {"plate_number", "capacity", "route_id"}
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if not updates:
            return make_response(message="No valid fields to update", status_code=400)

        for key, value in updates.items():
            setattr(matatu, key, value)

        try:
            db.session.commit()
            return make_response(
                message="Matatu updated successfully", 
                data=matatu.to_dict(), 
                status_code=200
            )
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

    def delete(self, matatu_id):
        """Remove a matatu from the system"""
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status_code=404)

        try:
            db.session.delete(matatu)
            db.session.commit()
            return make_response(message="Matatu deleted successfully", status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

# 2. Map the resources to specific URLs
api.add_resource(MatatuListResource, '/')
api.add_resource(MatatuResource, '/<int:matatu_id>')