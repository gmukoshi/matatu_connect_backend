from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.booking import Booking
from app.utils.responses import api_response
from app.utils.pagination import paginate
from app.extensions import db

class BookingResource(Resource):
    @jwt_required()
    def post(self):
        """Standardized response for creating a booking"""
        data = request.get_json()
        user_id = get_jwt_identity()

        # Check seat availability
        existing = Booking.query.filter_by(
            matatu_id=data['matatu_id'], 
            seat_number=data['seat_number'], 
            status='confirmed'
        ).first()
        
        if existing:
            return api_response("This seat is already booked", status="error", status_code=400)

        new_booking = Booking(
            user_id=user_id,
            matatu_id=data['matatu_id'],
            seat_number=data['seat_number'],
            status='pending'
        )
        db.session.add(new_booking)
        db.session.commit()

        return api_response(
            message="Booking created successfully",
            data=new_booking.to_dict(),
            status_code=201
        )

    @jwt_required()
    def get(self, booking_id=None):
        """Standardized response for fetching bookings (Single or List)"""
        user_id = get_jwt_identity()

        if booking_id:
            booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
            if not booking:
                return api_response("Booking not found", status="error", status_code=404)
            return api_response("Booking retrieved", data=booking.to_dict())

        # Paginated History
        page = request.args.get('page', 1, type=int)
        query = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc())
        paginated_data = paginate(query, page, per_page=5)
        
        return api_response("User booking history retrieved", data=paginated_data)