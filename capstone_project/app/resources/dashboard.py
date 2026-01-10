from flask import Blueprint
from flask_restful import Resource, Api
from datetime import date
from sqlalchemy import func

# Utility imports
from app.utils.responses import success_response, error_response
from app.extensions import db

# Model imports
from app.models.matatu import Matatu
from app.models.booking import Booking
from app.models.route import Route
from app.models.payment import Payment
from app.models.user import User

# Define Blueprint
dashboard_bp = Blueprint('dashboard_bp', __name__)
api = Api(dashboard_bp)

class DashboardStats(Resource):
    def get(self):
        try:
            # 1. Count Total Bookings
            total_bookings = Booking.query.count()

            # 2. Count Active Matatus (Assuming all in DB are active, or filter by status)
            active_matatus = Matatu.query.count()

            # 3. Calculate Revenue for Today
            # Sums the 'amount' column for payments created today
            revenue_today = db.session.query(func.sum(Payment.amount))\
                .filter(func.date(Payment.created_at) == date.today())\
                .filter(Payment.status == 'completed')\
                .scalar() or 0.0

            # 4. Count Total Registered Commuters
            total_users = User.query.filter_by(role='passenger').count()

            stats = {
                "total_bookings": total_bookings,
                "active_matatus": active_matatus,
                "revenue_today": float(revenue_today),
                "total_users": total_users,
                "system_health": "Optimal"
            }

            return success_response(
                data=stats, 
                message="Real-time dashboard stats synchronized"
            )
            
        except Exception as e:
            return error_response(
                message="Failed to load dashboard statistics", 
                error=str(e), 
                status_code=500
            )

# Register resource
api.add_resource(DashboardStats, '/stats')