from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.log import MatatuLog
from app.models.matatu import Matatu
from app.extensions import db
from app.utils.responses import success_response, error_response

log_bp = Blueprint('log_bp', __name__)
api = Api(log_bp)

class DriverLogResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
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

    @jwt_required()
    def get(self):
        # Fetch Filtered Logs
        user_identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        sacco_id = claims.get('sacco_id') # Managers usually have this in token
        
        if role == 'sacco_manager':
            # 1. Fetch by Sacco
            if not sacco_id:
                # Fallback: fetch User fresh
                user = User.query.get(int(user_identity))
                sacco_id = user.sacco_id
                
            if sacco_id:
                # Join with Matatu to filter by Sacco
                logs = MatatuLog.query.join(Matatu).filter(Matatu.sacco_id == sacco_id).order_by(MatatuLog.created_at.desc()).all()
            else:
                logs = []
        elif role == 'driver':
            # 2. Fetch by Driver (Own logs)
            logs = MatatuLog.query.filter_by(driver_id=int(user_identity)).order_by(MatatuLog.created_at.desc()).all()
        else:
            return error_response("Unauthorized", 403)
            
        return success_response(data=[l.to_dict() for l in logs], message="Logs retrieved")

api.add_resource(DriverLogResource, '/')
