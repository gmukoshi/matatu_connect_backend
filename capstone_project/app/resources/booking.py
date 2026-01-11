from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.booking import Booking
from ..extensions import db
from ..utils.responses import success_response, error_response

booking_bp = Blueprint('booking_bp', __name__)
api = Api(booking_bp)

from ..models.matatu import Matatu

class BookingListResource(Resource):
    @jwt_required()
    def get(self):
        """Commuters see their own, Admins see all, Drivers see their bus's"""
        user_info = get_jwt_identity()
        role = user_info.get('role')
        user_id = user_info['id']

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
        user_info = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('matatu_id') or not data.get('seat_number'):
            return error_response("matatu_id and seat_number required", 400)

        new_booking = Booking(
            user_id=user_info['id'],
            matatu_id=data['matatu_id'],
            seat_number=data['seat_number'],
            status='pending'
        )

        try:
            db.session.add(new_booking)
            db.session.commit()
            return success_response(data=new_booking.to_dict(), message="Booking created", status_code=201)
        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

class BookingActionResource(Resource):
    @jwt_required()
    def post(self, booking_id, action):
        user_info = get_jwt_identity()
        user_id = user_info['id']
        role = user_info.get('role')

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
        return success_response(data=booking.to_dict(), message=f"Booking {action}ed")

api.add_resource(BookingListResource, '/')
api.add_resource(BookingActionResource, '/<int:booking_id>/<string:action>')