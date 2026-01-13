from flask import request, Blueprint, abort
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.matatu import Matatu
from ..models.user import User
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

    @jwt_required()
    def post(self):
        try:
            data = request.get_json() or {}
            if not data.get("plate_number"):
                return error_response("Plate number is required", 400)

            current_identity = get_jwt_identity()
            # Handle both identity formats (some versions return string, others dict)
            user_id = current_identity['id'] if isinstance(current_identity, dict) else current_identity
            
            user = db.session.get(User, user_id)
            if not user:
                 return error_response("User not found", 404)
            
            # Determine Sacco ID
            sacco_id = data.get("sacco_id")
            
            # If Manager, enforce their Sacco
            if user.role == User.ROLE_SACCO_MANAGER:
                if not user.sacco_id:
                    return error_response("Manager has no Sacco assigned", 403)
                sacco_id = user.sacco_id
                
            # If Driver/Commuter, deny
            elif user.role not in [User.ROLE_ADMIN, User.ROLE_SACCO_MANAGER]:
                 return error_response("Unauthorized to add vehicles", 403)
                 
            # If Admin (or allowed others), require explicit sacco_id
            if not sacco_id:
                 return error_response("Sacco ID required", 400)

            new_matatu = Matatu(
                plate_number=data["plate_number"],
                capacity=data.get("capacity", 14),
                route_id=data.get("route_id"),
                sacco_id=sacco_id,
                driver_id=data.get("driver_id")
            )
            
            db.session.add(new_matatu)
            db.session.commit()
            return success_response(data=new_matatu.to_dict(), status_code=201)
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc() # Print to server logs
            return error_response(f"Server error: {str(e)}", 500)

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

    @jwt_required()
    def delete(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            abort(404)
        
        # Manual Cascade Delete for Bookings AND Payments
        from ..models.booking import Booking
        from ..models.payment import Payment
        
        try:
            # 1. Find Bookings
            bookings = Booking.query.filter_by(matatu_id=matatu_id).all()
            booking_ids = [b.id for b in bookings]
            
            if booking_ids:
                # 2. Delete Payments linked to these bookings
                Payment.query.filter(Payment.booking_id.in_(booking_ids)).delete(synchronize_session=False)
                
                # 3. Delete Bookings
                Booking.query.filter(Booking.id.in_(booking_ids)).delete(synchronize_session=False)
            
            # 4. Delete Matatu
            db.session.delete(matatu)
            db.session.commit()
            return success_response(data=None, message="Matatu deleted")
        except Exception as e:
            db.session.rollback()
            return error_response(f"Delete failed: {str(e)}", 500)

class MatatuAcceptResource(Resource):
    @jwt_required()
    def post(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            return error_response("Matatu not found", 404)
        
        current_identity = get_jwt_identity()
        user_id = current_identity['id'] if isinstance(current_identity, dict) else current_identity
        
        # Verify the user is the assigned driver
        if matatu.driver_id != user_id:
            return error_response("Unauthorized: You are not assigned to this vehicle", 403)

        matatu.assignment_status = "active"
        db.session.commit()
        return success_response(data=matatu.to_dict(), message="Assignment accepted")

class MatatuRejectResource(Resource):
    @jwt_required()
    def post(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            return error_response("Matatu not found", 404)

        current_identity = get_jwt_identity()
        user_id = current_identity['id'] if isinstance(current_identity, dict) else current_identity
        
        # Verify the user is the assigned driver
        if matatu.driver_id != user_id:
            return error_response("Unauthorized: You are not assigned to this vehicle", 403)
        
        matatu.assignment_status = "rejected"
        matatu.driver_id = None # Unassign driver
        db.session.commit()
        return success_response(data=matatu.to_dict(), message="Assignment rejected")

api.add_resource(MatatuListResource, '/')
api.add_resource(MatatuResource, '/<int:matatu_id>')
api.add_resource(MatatuAcceptResource, '/<int:matatu_id>/accept')
api.add_resource(MatatuRejectResource, '/<int:matatu_id>/reject')