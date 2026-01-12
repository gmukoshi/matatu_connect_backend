from flask import Blueprint, jsonify
from app.models.user import User
from app.services.auth_service import admin_required, sacco_manager_required

user_bp = Blueprint('user_mgmt', __name__)

# ADMIN ONLY: View all users
@user_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

from flask_jwt_extended import get_jwt_identity

# SACCO MANAGER ONLY: View drivers in their Sacco
@user_bp.route('/manager/drivers', methods=['GET'])
@sacco_manager_required
def get_sacco_drivers():
    current_user = get_jwt_identity()
    user = db.session.get(User, current_user['id'])
    
    if not user or not user.sacco_id:
        return jsonify([])

    drivers = User.query.filter_by(role=User.ROLE_DRIVER, sacco_id=user.sacco_id).all()
    
    # Enhanced driver list with vehicle and route info
    driver_list = []
    for d in drivers:
        d_dict = d.to_dict()
        # Find active assigned vehicle
        # We can look up Matatu where driver_id match. 
        # Since logic might be 1:1 active, let's find the first associated matatu
        vehicle = next((m for m in d.matatus if m.assignment_status == 'active'), None)
        
        if vehicle:
            d_dict['assigned_vehicle'] = vehicle.plate_number
            d_dict['assigned_route'] = vehicle.route.name if vehicle.route else None
        else:
            d_dict['assigned_vehicle'] = None
            d_dict['assigned_route'] = None
            
        driver_list.append(d_dict)

    return jsonify(driver_list), 200

from flask import request
from flask_restful import Resource, Api
from ..models.user import User
from ..extensions import db
from ..utils.responses import make_response

api = Api(user_bp)

class UserListResource(Resource):
    # Optional: admin only
    def get(self):
        users = User.query.all()
        return make_response(
            message="Users fetched successfully",
            data=[u.to_dict() for u in users],
            status_code=200
        )

class UserResource(Resource):
    # Optional: public profile or admin fetch
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status_code=404)
        return make_response(message="User fetched successfully", data=user.to_dict(), status_code=200)

    # Optional: admin delete
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status_code=404)

        try:
            db.session.delete(user)
            db.session.commit()
            return make_response(message="User deleted successfully", status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

class RegisterResource(Resource):
    def post(self):
        data = request.get_json() or {}
        required = ("username", "email", "password")
        if not all(k in data for k in required):
            return make_response(
                message="Validation Error",
                error="Missing fields: username, email, password",
                status_code=400
            )

        if User.query.filter_by(email=data["email"]).first():
            return make_response(message="Conflict", error="Email already exists", status_code=409)

        # Validate role
        role = data.get("role", "commuter")  # Default to commuter
        sacco_name = data.get("sacco_name")

        user = User(username=data["username"], email=data["email"], role=role)
        user.set_password(data["password"])

        try:
            db.session.add(user)
            db.session.flush() # access user.id

            # Handle Sacco Manager Registration
            if role == User.ROLE_SACCO_MANAGER and sacco_name:
                from ..models.sacco import Sacco
                
                # Check if sacco exists or create new
                sacco = Sacco.query.filter_by(name=sacco_name).first()
                if not sacco:
                    sacco = Sacco(name=sacco_name)
                    db.session.add(sacco)
                    db.session.flush() # access sacco.id
                
                user.sacco_id = sacco.id

            db.session.commit()
            return make_response(message="User registered successfully", data=user.to_dict(), status_code=201)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

class DriverSearchResource(Resource):
    @sacco_manager_required
    def get(self):
        email = request.args.get('email')
        if not email:
            return make_response(message="Bad Request", error="Email query parameter required", status_code=400)
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(message="Not Found", error="Driver not found", status_code=404)
            
        if user.role != User.ROLE_DRIVER:
            return make_response(message="Invalid Role", error="User is not a driver", status_code=400)
            
        # Return preview details
        return make_response(
            message="Driver found",
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "license_number": user.license_number,
                "sacco_id": user.sacco_id,
                "verification_status": user.verification_status
            },
            status_code=200
        )

class DriverInviteResource(Resource):
    @sacco_manager_required
    def post(self):
        data = request.get_json()
        email = data.get("email")
        
        if not email:
            return make_response(message="Bad Request", error="Email is required", status_code=400)
            
        user = User.query.filter_by(email=email).first()
        if not user:
             return make_response(message="Not Found", error="Driver not found with that email", status_code=404)
        
        if user.role != User.ROLE_DRIVER:
             return make_response(message="Invalid Role", error="User is not a driver", status_code=400)
             
        current_user = get_jwt_identity()
        manager = db.session.get(User, current_user['id'])
        
        if not manager.sacco_id:
             return make_response(message="Config Error", error="Manager has no Sacco assigned", status_code=500)

        user.sacco_id = manager.sacco_id
        # Reset status to pending so manager sees them and must approve (verifying license again effectively)
        # OR keep 'approved' if they trust the invite? 
        # User asked: "verify... before accepting". 
        # So we add them, but maybe status should be 'pending'? 
        # If I strictly follow: "Add Existing" -> They become part of Sacco.
        # The Verification step happens IN THE MODAL before this POST is called.
        # So here we can just add them. Let's keep status as is or 'approved' to avoid workflow friction if they verified visually?
        # Actually better to set 'approved' if the manager explicitly "Adds" them after seeing the license.
        user.verification_status = "approved"
        
        try:
            db.session.commit()
            return make_response(message="Driver added to Sacco successfully", data=user.to_dict(), status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

class DriverActionResource(Resource):
    @sacco_manager_required
    def post(self, user_id, action):
        current_user = get_jwt_identity()
        manager = db.session.get(User, current_user['id'])
        
        user = db.session.get(User, user_id)
        if not user:
             return make_response(message="Not Found", error="Driver not found", status_code=404)
        
        if user.role != User.ROLE_DRIVER:
             return make_response(message="Invalid Role", error="User is not a driver", status_code=400)

        if action == "approve":
            user.verification_status = "approved"
            # Auto-assign to manager's Sacco if not already assigned
            if not user.sacco_id and manager.sacco_id:
                user.sacco_id = manager.sacco_id
                
        elif action == "reject":
            user.verification_status = "rejected"
        else:
            return make_response(message="Invalid Action", error="Action must be approve or reject", status_code=400)
            
        try:
            db.session.commit()
            return make_response(message=f"Driver {action}d successfully", data=user.to_dict(), status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

api.add_resource(UserListResource, '/')
api.add_resource(UserResource, '/<int:user_id>')
api.add_resource(RegisterResource, '/register')
api.add_resource(DriverInviteResource, '/manager/invite')
api.add_resource(DriverSearchResource, '/manager/drivers/search')
api.add_resource(DriverActionResource, '/manager/drivers/<int:user_id>/<string:action>')
