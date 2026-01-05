from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.utils.responses import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def sacco_dashboard_summary():
    """
    Sacco Admin Dashboard Summary
    Returns:
    - Total Revenue
    - Total Bookings
    """

    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        return error_response("User not found", 404)

    if user.role != "sacco_admin":
        return error_response("Access denied", 403)

    sacco_id = user.sacco_id

    # ---------------------------
    # Total Bookings
    # ---------------------------
    total_bookings = (
        db.session.query(func.count(Booking.id))
        .filter(
            Booking.sacco_id == sacco_id,
            Booking.status == "completed"
        )
        .scalar()
    )

    # ---------------------------
    # Total Revenue
    # ---------------------------
    total_revenue = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.sacco_id == sacco_id,
            Payment.status == "paid"
        )
        .scalar()
    )

    data = {
        "total_revenue": float(total_revenue),
        "total_bookings": total_bookings
    }

    return success_response(data, "Dashboard summary fetched successfully")
