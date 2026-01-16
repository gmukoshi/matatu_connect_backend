from flask import Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import sacco_manager_required
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
from app.models.log import MatatuLog

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

class SaccoDashboardStats(Resource):
    @sacco_manager_required
    def get(self):
        try:
            user_info = get_jwt_identity()
            # In a real app, you'd fetch the user obj if sacco_id isn't in JWT
            # Assuming sacco_id is in JWT or we fetch User
            user = db.session.get(User, user_info['id'])
            if not user or not user.sacco_id:
                return error_response("User is not assigned to a Sacco", status_code=400)
            
            sacco_id = user.sacco_id
            
            # Calculate Total Revenue for this Sacco
            # Filter Payments -> Bookings -> Matatu -> Sacco
            total_revenue = db.session.query(func.sum(Payment.amount))\
                .join(Booking, Payment.booking_id == Booking.id)\
                .join(Matatu, Booking.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .filter(Payment.status == 'completed')\
                .scalar() or 0.0

            # Active Fleet (vehicles assigned and active)
            # User Change (Step 673): "active fleet should fetch available drivers"
            # We will use Total Drivers as "Active Fleet" for now, or drivers with assigned vehicles if preferred.
            # Assuming 'Active Fleet' text on frontend now represents 'Available Drivers'
            
            # Count drivers in this Sacco
            # Active Fleet (Drivers)
            # Count ALL drivers linked to this Sacco (whether assigned a vehicle or not) to show "Available Workforce"
            active_drivers = User.query.filter_by(sacco_id=sacco_id, role='driver').count()
            active_fleet_count = active_drivers

            # Daily Passengers (from logs today)
            daily_passengers = db.session.query(func.sum(MatatuLog.passengers_carried))\
                .join(Matatu, MatatuLog.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .filter(MatatuLog.log_date == date.today())\
                .scalar() or 0

            # Fuel Efficiency (Total Mileage / Total Fuel)
            # Calculated from logs
            total_mileage_logs = db.session.query(func.sum(MatatuLog.mileage_km))\
                .join(Matatu, MatatuLog.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .scalar() or 0.0
            
            total_fuel_logs = db.session.query(func.sum(MatatuLog.fuel_liters))\
                .join(Matatu, MatatuLog.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .scalar() or 0.0

            fuel_efficiency = round(total_mileage_logs / total_fuel_logs, 1) if total_fuel_logs > 0 else 0.0
            
            # Total Drivers in Sacco
            # Assuming User model refers to Sacco (sacco_id) or we look at Matatu.driver_id... 
            # But the most accurate "Sacco Drivers" is Users with role 'driver' and sacco_id attached.
            total_drivers = User.query.filter_by(sacco_id=sacco_id, role='driver').count()

            # 7-Day Revenue Trend
            from datetime import timedelta
            revenue_trend = []
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # --- COMPARISON LOGIC ---
            
            # 1. Revenue Comparison
            revenue_today = db.session.query(func.sum(Payment.amount))\
                .join(Booking, Payment.booking_id == Booking.id)\
                .join(Matatu, Booking.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .filter(func.date(Payment.created_at) == today)\
                .filter(Payment.status == 'completed')\
                .scalar() or 0.0

            revenue_yesterday = db.session.query(func.sum(Payment.amount))\
                .join(Booking, Payment.booking_id == Booking.id)\
                .join(Matatu, Booking.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .filter(func.date(Payment.created_at) == yesterday)\
                .filter(Payment.status == 'completed')\
                .scalar() or 0.0
                
            if revenue_yesterday > 0:
                revenue_growth = ((revenue_today - revenue_yesterday) / revenue_yesterday) * 100
            else:
                revenue_growth = 100.0 if revenue_today > 0 else 0.0

            # 2. Passenger Comparison
            passengers_today = daily_passengers # Already calculated above (lines 89-94)
            
            passengers_yesterday = db.session.query(func.sum(MatatuLog.passengers_carried))\
                .join(Matatu, MatatuLog.matatu_id == Matatu.id)\
                .filter(Matatu.sacco_id == sacco_id)\
                .filter(MatatuLog.log_date == yesterday)\
                .scalar() or 0
            
            if passengers_yesterday > 0:
                passenger_growth = ((passengers_today - passengers_yesterday) / passengers_yesterday) * 100
            else:
                passenger_growth = 100.0 if passengers_today > 0 else 0.0

            # Trend Array Construction
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                day_revenue = db.session.query(func.sum(Payment.amount))\
                    .join(Booking, Payment.booking_id == Booking.id)\
                    .join(Matatu, Booking.matatu_id == Matatu.id)\
                    .filter(Matatu.sacco_id == sacco_id)\
                    .filter(func.date(Payment.created_at) == day)\
                    .filter(Payment.status == 'completed')\
                    .scalar() or 0.0
                
                revenue_trend.append({
                    "name": day.strftime("%a"), # Mon, Tue...
                    "revenue": float(day_revenue)
                })

            stats = {
                "total_revenue": float(total_revenue),
                "total_revenue": float(total_revenue),
                "active_fleet": f"{active_fleet_count} Drivers", # Simplified as requested
                # "active_fleet": f"{active_fleet_count}/{total_fleet_count}", # Old vehicle format
                "daily_passengers": int(daily_passengers),
                "fuel_efficiency": f"{fuel_efficiency} km/L",
                "total_drivers": total_drivers,
                "revenue_trend": revenue_trend,
                # New Fields
                "revenue_growth": round(revenue_growth, 1),
                "passenger_growth": round(passenger_growth, 1),
                "revenue_today": float(revenue_today),
                "revenue_yesterday": float(revenue_yesterday)
            }
            
            return success_response(data=stats, message="Sacco stats retrieved")

        except Exception as e:
            return error_response("Failed to load sacco stats", error=str(e), status_code=500)

# Register resource
api.add_resource(DashboardStats, '/stats')
api.add_resource(SaccoDashboardStats, '/sacco-stats')