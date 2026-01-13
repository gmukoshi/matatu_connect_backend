from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.sacco import Sacco
from app.models.user import User
from app.extensions import db
from app.utils.responses import success_response, error_response
from app.services.auth_service import sacco_manager_required

sacco_bp = Blueprint('sacco_bp', __name__)
api = Api(sacco_bp)

class SaccoListResource(Resource):
    def get(self):
        """List all available saccos"""
        try:
            saccos = Sacco.query.all()
            return success_response(
                data=[s.to_dict() for s in saccos], 
                message="Saccos retrieved successfully"
            )
        except Exception as e:
            return error_response(message="Failed to fetch saccos", error=str(e), status_code=500)

class SaccoAssignmentResource(Resource):
    @sacco_manager_required
    def post(self):
        """Assign current manager to a sacco"""
        try:
            user_identity = get_jwt_identity()
            user_id = user_identity['id']
            
            data = request.get_json() or {}
            sacco_id = data.get('sacco_id')
            
            if not sacco_id:
                return error_response(message="Sacco ID is required", status_code=400)
            
            sacco = db.session.get(Sacco, sacco_id)
            if not sacco:
                return error_response(message="Sacco not found", status_code=404)
                
            user = db.session.get(User, user_id)
            if not user:
                return error_response(message="User not found", status_code=404)
            
            user.sacco_id = sacco.id
            db.session.commit()
            
            return success_response(
                # Refresh user identity/token logic might be needed on frontend
                data={"sacco": sacco.to_dict(), "user": user.to_dict()}, 
                message=f"Successfully joined {sacco.name}"
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(message="Failed to assign sacco", error=str(e), status_code=500)

api.add_resource(SaccoListResource, '')
api.add_resource(SaccoAssignmentResource, '/assign')
