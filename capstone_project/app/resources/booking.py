from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models.booking import Booking
from ..extensions import db, socketio
from ..utils.responses import success_response, error_response

booking_bp = Blueprint('booking_bp', __name__)
api = Api(booking_bp)

from ..models.matatu import Matatu

class BookingListResource(Resource):
    @jwt_required()
    def get(self):
        """Commuters see their own, Admins see all, Drivers see their bus's"""
        current_identity = get_jwt_identity()
        try:
             user_id = int(current_identity)
        except ValueError:
             return error_response("Invalid User ID in token", 401)
        
        claims = get_jwt()
        role = claims.get('role')

        # The original `get` method for BookingListResource did not take a matatu_id.
        # This `if matatu_id:` block seems misplaced if it's intended for this resource.
        # Assuming it's a comment or placeholder for future logic,
        # and the primary goal is to update identity parsing and role extraction.
        # The existing logic for admin/driver/commuter will be adapted to the new user_id/role.
        # If the intent was to merge with MatatuBookingsResource, that's a larger change.
        # For now, I will integrate the identity parsing and keep the original logic flow.

        if role == 'admin':
            bookings = Booking.query.all()
        elif role == 'driver':
            # Find the matatu assigned to this driver
            matatu = Matatu.query.filter_by(driver_id=user_id).first()
            if not matatu:
                return success_response(data=[], message="No vehicle assigned")
            
            # Find bookings for this matatu
            bookings = Booking.query.filter_by(matatu_id=matatu.id).all()
        else:
            # Commuter (or default)
            bookings = Booking.query.filter_by(user_id=user_id).all()
        
        return success_response(data=[b.to_dict() for b in bookings], message="Bookings retrieved")

    @jwt_required()
    def post(self):
        data = request.get_json()
        
        if not data.get('matatu_id') or not data.get('seat_number'):
            return error_response("matatu_id and seat_number required", 400)

        user_id = get_jwt_identity()
        try:
             user_id = int(user_id)
        except ValueError:
             return error_response("Invalid User ID in token", 401)

        new_booking = Booking(
            user_id=user_id,
            matatu_id=data['matatu_id'],
            seat_number=data['seat_number'],
            status='pending'
        )

        try:
            db.session.add(new_booking)
            db.session.commit()

            # Emit socket event to the Driver (via Matatu room)
            socketio.emit('new_booking', new_booking.to_dict(), room=f"matatu_{new_booking.matatu_id}")

            return success_response(data=new_booking.to_dict(), message="Booking created", status_code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

class BookingActionResource(Resource):
    @jwt_required()
    def post(self, booking_id, action):
        current_identity = get_jwt_identity()
        if not current_identity:
             return error_response("Missing identity", 401)
        try:
             user_id = int(current_identity)
        except ValueError:
             return error_response("Invalid ID", 401)
             
        claims = get_jwt()
        role = claims.get('role')

        booking = db.session.get(Booking, booking_id)
        if not booking:
            return error_response("Booking not found", 404)

        # Authorization: Only the assigned driver (or admin) can accept/reject
        if role == 'driver':
             matatu = Matatu.query.filter_by(driver_id=user_id).first()
             if not matatu or matatu.id != booking.matatu_id:
                 return error_response("Unauthorized: You are not the driver of this vehicle", 403)
        elif role != 'admin':
             return error_response("Unauthorized", 403)

        if action == 'accept':
            booking.status = 'confirmed'
        elif action == 'reject':
            booking.status = 'rejected'
        else:
            return error_response("Invalid action", 400)

        db.session.commit()

        # Emit socket event to the Commuter (via User room)
        socketio.emit('booking_status_update', booking.to_dict(), room=f"user_{booking.user_id}")
        
        # Emit to Matatu room (for Driver Dashboard & other Commuters viewing the vehicle)
        socketio.emit('booking_updated', booking.to_dict(), room=f"matatu_{booking.matatu_id}")

        return success_response(data=booking.to_dict(), message=f"Booking {action}ed")

class MatatuBookingsResource(Resource):
    """Get all bookings for a specific matatu (for seat status visualization)"""
    def get(self, matatu_id):
        try:
            matatu = db.session.get(Matatu, matatu_id)
            if not matatu:
                return error_response("Matatu not found", 404)
            
            # Get all bookings for this matatu (pending and confirmed)
            bookings = Booking.query.filter_by(matatu_id=matatu_id).filter(
                Booking.status.in_(['pending', 'confirmed'])
            ).all()
            
            return success_response(data=[b.to_dict() for b in bookings], message="Matatu bookings retrieved")
        except Exception as e:
            return error_response(str(e), 500)

class TripCompletionResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')

        if role != 'driver':
            return error_response("Unauthorized: Only drivers can complete trips", 403)

        try:
            # Find the matatu assigned to this driver
            matatu = Matatu.query.filter_by(driver_id=user_id).first()
            if not matatu:
                return error_response("No vehicle assigned to this driver", 404)

            # Find all active bookings (confirmed)
            # We might also want to mark 'pending' ones as 'rejected' or just leave them?
            # Let's say we complete confirmed ones.
            active_bookings = Booking.query.filter_by(matatu_id=matatu.id, status='confirmed').all()
            
            if not active_bookings:
                return success_response(message="No active bookings to complete")

            count = 0
            for booking in active_bookings:
                booking.status = 'completed'
                count += 1
                
                # Notify User
                socketio.emit('booking_status_update', booking.to_dict(), room=f"user_{booking.user_id}")
            
            db.session.commit()
            
            # Notify Driver/Matatu room
            socketio.emit('trip_completed', {"matatu_id": matatu.id, "count": count}, room=f"matatu_{matatu.id}")

            return success_response(data={"count": count}, message=f"Trip completed. {count} bookings marked as completed.")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

api.add_resource(BookingListResource, '/')
api.add_resource(BookingActionResource, '/<int:booking_id>/<string:action>')
api.add_resource(MatatuBookingsResource, '/matatu/<int:matatu_id>')
api.add_resource(TripCompletionResource, '/complete_trip')