from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.log import MatatuLog
from app.models.matatu import Matatu
from app.extensions import db
from app.utils.responses import success_response, error_response

log_bp = Blueprint('log_bp', __name__)
api = Api(log_bp)

class DriverLogResource(Resource):
    @jwt_required()
    def post(self):
        user_info = get_jwt_identity()
        user_id = user_info['id']
        role = user_info.get('role')
        
        if role != 'driver':
             return error_response("Unauthorized: Only drivers can submit logs", 403)

        data = request.get_json() or {}
        
        # Validate inputs
        passengers = data.get('passengers')
        fuel = data.get('fuel')
        mileage = data.get('mileage')
        
        if passengers is None or fuel is None or mileage is None:
            return error_response("Missing details (passengers, fuel, mileage)", 400)
            
        # Find assigned Matatu
        matatu = Matatu.query.filter_by(driver_id=user_id).first()
        if not matatu:
            return error_response("No vehicle assigned to this driver", 404)
        
        try:
            new_log = MatatuLog(
                matatu_id=matatu.id,
                driver_id=user_id,
                passengers_carried=int(passengers),
                fuel_liters=float(fuel),
                mileage_km=float(mileage)
            )
            
            new_log.save()
            
            return success_response(message="Daily log submitted successfully", data=new_log.to_dict(), status_code=201)
            
        except Exception as e:
            return error_response(f"Failed to submit log: {str(e)}", 500)

api.add_resource(DriverLogResource, '/')
