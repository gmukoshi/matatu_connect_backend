from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.booking import Booking
from ..extensions import db
from ..utils.responses import success_response, error_response

booking_bp = Blueprint('booking_bp', __name__)
api = Api(booking_bp)

class BookingListResource(Resource):
    @jwt_required()
    def get(self):
        """Commuters see their own, Admins see all"""
        user_info = get_jwt_identity()
        if user_info['role'] == 'admin':
            bookings = Booking.query.all()
        else:
            bookings = Booking.query.filter_by(user_id=user_info['id']).all()
        
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

api.add_resource(BookingListResource, '/')