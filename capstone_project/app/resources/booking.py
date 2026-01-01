from flask import Blueprint, jsonify

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/", methods=["GET"])
def get_bookings():
    return jsonify({"message": "List of bookings"})
