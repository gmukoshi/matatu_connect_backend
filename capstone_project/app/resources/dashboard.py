from flask import Blueprint
from flask_restful import Resource, Api
from app.utils.responses import success_response, error_response
# Import your models here to get stats (e.g., from app.models.matatu import Matatu)

dashboard_bp = Blueprint('dashboard_bp', __name__)
api = Api(dashboard_bp)

class DashboardStats(Resource):
    def get(self):
        try:
            # Example stats for your fintech dashboard
            stats = {
                "total_bookings": 150,
                "active_matatus": 12,
                "revenue_today": 4500.00
            }
            return success_response(data=stats, message="Dashboard stats fetched")
        except Exception as e:
            return error_response(message="Failed to load dashboard", error=str(e))

api.add_resource(DashboardStats, '/stats')