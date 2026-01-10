from flask import request, Blueprint, abort
from flask_restful import Resource, Api
from ..models.matatu import Matatu
from ..extensions import db
from ..utils.responses import success_response, error_response

matatu_bp = Blueprint('matatu_bp', __name__)
api = Api(matatu_bp)

class MatatuListResource(Resource):
    def get(self):
        matatus = Matatu.query.all()
        # Ensure success_response returns a dict, not a Response object
        return success_response(
            data=[m.to_dict() for m in matatus], 
            message="Success"
        )

    def post(self):
        data = request.get_json() or {}
        if not data.get("plate_number") or not data.get("sacco_id"):
            return error_response("Plate number and Sacco ID required", 400)

        new_matatu = Matatu(
            plate_number=data["plate_number"],
            capacity=data.get("capacity", 14),
            route_id=data.get("route_id"),
            sacco_id=data["sacco_id"],
            driver_id=data.get("driver_id")
        )
        try:
            db.session.add(new_matatu)
            db.session.commit()
            return success_response(data=new_matatu.to_dict(), status_code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Database error: {str(e)}", 500)

class MatatuResource(Resource):
    def get(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            abort(404)
        return success_response(data=matatu.to_dict())

    def patch(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            abort(404)
        data = request.get_json() or {}

        if "capacity" in data:
            matatu.capacity = data["capacity"]
        if "route_id" in data:
            matatu.route_id = data["route_id"]
        if "driver_id" in data:
            matatu.driver_id = data["driver_id"]
            matatu.assignment_status = "pending" # Reset status on new assignment

        db.session.commit()
        return success_response(data=matatu.to_dict(), message="Matatu updated")

    def delete(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            abort(404)
        db.session.delete(matatu)
        db.session.commit()
        return success_response(data=None, message="Matatu deleted")

class MatatuAcceptResource(Resource):
    def post(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            return error_response("Matatu not found", 404)
        
        # In real app, check if current_user.id == matatu.driver_id

        matatu.assignment_status = "active"
        db.session.commit()
        return success_response(data=matatu.to_dict(), message="Assignment accepted")

class MatatuRejectResource(Resource):
    def post(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            return error_response("Matatu not found", 404)

        # In real app, check ownership
        
        matatu.assignment_status = "rejected"
        matatu.driver_id = None # Unassign driver
        db.session.commit()
        return success_response(data=matatu.to_dict(), message="Assignment rejected")

api.add_resource(MatatuListResource, '/')
api.add_resource(MatatuResource, '/<int:matatu_id>')
api.add_resource(MatatuAcceptResource, '/<int:matatu_id>/accept')
api.add_resource(MatatuRejectResource, '/<int:matatu_id>/reject')