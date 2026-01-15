from flask import request, Blueprint, abort
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.matatu import Matatu
from ..models.user import User
from ..extensions import db
from ..utils.responses import success_response, error_response
from ..utils.email import send_email

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

            current_user_id = get_jwt_identity()
            # New JWT structure: identity is always a string ID
            user_id = current_user_id
            
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
            
            # Send Email to Assigned Driver
            if new_matatu.driver_id:
                driver = db.session.get(User, new_matatu.driver_id)
                if driver:
                    try:
                        send_email(
                            driver.email, 
                            "New Vehicle Assignment - Matatu Connect",
                            f"<h3>Hello {driver.name},</h3><p>You have been assigned to vehicle <b>{new_matatu.plate_number}</b>.</p><p>Please log in to your dashboard to accept or reject this assignment.</p>"
                        )
                    except Exception as e:
                        print(f"Warning: Email sending failed: {e}")
            
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
            
            # Send Email to Assigned Driver
            print(f"DEBUG: Matatu {matatu.id} PATCH received. Data keys: {data.keys()}")
            print(f"DEBUG: driver_id in data: {'driver_id' in data}")
            if 'driver_id' in data:
                 print(f"DEBUG: driver_id value: {data['driver_id']}")

            driver = db.session.get(User, data["driver_id"])
            if driver:
                print(f"DEBUG: Attempting to send email to {driver.email}")
                email_sent = send_email(
                    driver.email, 
                    "New Vehicle Assignment - Matatu Connect",
                    f"<h3>Hello {driver.name},</h3><p>You have been assigned to vehicle <b>{matatu.plate_number}</b>.</p><p>Please log in to your dashboard to accept or reject this assignment.</p>"
                )
                print(f"DEBUG: SendGrid Result: {email_sent}")
            else:
                print("DEBUG: Driver not found in DB")

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
        
        current_user_id = get_jwt_identity()
        try:
             user_id = int(current_user_id)
        except ValueError:
             return error_response("Invalid User ID in token", 401)
        
        # Verify the user is the assigned driver
        if matatu.driver_id != user_id:
            return error_response("Unauthorized: You are not assigned to this vehicle", 403)

        matatu.assignment_status = "active"
        db.session.commit()
        
        # Notify Manager
        manager = None
        if matatu.sacco:
            # Logic to find manager - simplified assuming 1 manager per sacco or just notifying Sacco email if existed
            # For now, let's just log it if we can't find a direct manager email easily without Sacco model
            pass
            
        try:
            driver = db.session.get(User, user_id)
            driver_email = driver.email if driver else "driver@matatu.com"

            send_email(
                driver_email,
                "Assignment Accepted",
                f"You have successfully accepted assignment for {matatu.plate_number}."
            )
        except Exception as e:
            print(f"Warning: Email notification failed: {e}")

        return success_response(data=matatu.to_dict(), message="Assignment accepted")

class MatatuRejectResource(Resource):
    @jwt_required()
    def post(self, matatu_id):
        matatu = db.session.get(Matatu, matatu_id)
        if not matatu:
            return error_response("Matatu not found", 404)

        current_user_id = get_jwt_identity()
        try:
             user_id = int(current_user_id)
        except ValueError:
             return error_response("Invalid User ID in token", 401)
        
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