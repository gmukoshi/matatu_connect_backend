from flask import Blueprint, request
from flask_restful import Api, Resource
from app.utils.responses import api_response, error_response
from app.models.booking import Booking
from app.extensions import db

booking_bp = Blueprint('booking_bp', __name__)
api = Api(booking_bp)

class BookingListResource(Resource):
    def get(self):
        bookings = Booking.query.all()
        return api_response(data=[b.to_dict() for b in bookings], message="Bookings retrieved")

api.add_resource(BookingListResource, '/')