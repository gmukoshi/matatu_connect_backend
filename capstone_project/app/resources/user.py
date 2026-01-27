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
    # Identity is now User ID String
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    print(f"DEBUG: Fetching drivers for Manager ID: {user.id}, Sacco ID: {user.sacco_id}")

    if not user or not user.sacco_id:
        print("DEBUG: Manager has no Sacco ID. Returning empty list.")
        return jsonify([])

    drivers = User.query.filter_by(role=User.ROLE_DRIVER, sacco_id=user.sacco_id).all()
    print(f"DEBUG: Found {len(drivers)} drivers for Sacco {user.sacco_id}")
    
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
            d_dict['assigned_route'] = f"{vehicle.route.origin} - {vehicle.route.destination}" if vehicle.route else None
        else:
            d_dict['assigned_vehicle'] = None
            d_dict['assigned_route'] = None
            
        driver_list.append(d_dict)

    return jsonify(driver_list), 200

from flask import request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..extensions import db
from ..utils.responses import make_response

api = Api(user_bp)

class UserListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        current_user = db.session.get(User, current_user_id)
        
        if not current_user:
             return make_response(message="Unauthorized", status_code=401)

        if current_user.role == User.ROLE_SACCO_MANAGER:
            # Filter by Sacco
            if not current_user.sacco_id:
                return make_response(message="Users fetched successfully", data=[], status_code=200)
            users = User.query.filter_by(sacco_id=current_user.sacco_id).all()
            
        elif current_user.role == User.ROLE_ADMIN:
            users = User.query.all()
            
        else:
            # Commuters/Drivers shouldn't list all users
            return make_response(message="Forbidden", error="Access denied", status_code=403)

        return make_response(
            message="Users fetched successfully",
            data=[u.to_dict() for u in users],
            status_code=200
        )

class UserResource(Resource):
    # Optional: public profile or admin fetch
    @jwt_required()
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status_code=404)
        return make_response(message="User fetched successfully", data=user.to_dict(), status_code=200)

    @jwt_required()
    def delete(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = db.session.get(User, current_user_id) # ID is string from identity
        
        user_to_delete = db.session.get(User, user_id)
        if not user_to_delete:
            return make_response(message="Not found", error="User not found", status_code=404)

        # Permission Check: Self or Admin
        # Convert IDs to string/int consistently for comparison
        if str(current_user.id) != str(user_id) and current_user.role != User.ROLE_ADMIN:
             return make_response(message="Forbidden", error="You can only delete your own account", status_code=403)

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            return make_response(message="Account deleted successfully", status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

from ..utils.validators import validate_password # Imported validator

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

        # Validate Password Strength
        _, password_error = validate_password(data["password"])
        if password_error:
            return make_response(
                message="Validation Error",
                error=password_error,
                status_code=400
            )

        if User.query.filter_by(email=data["email"]).first():
            return make_response(message="Conflict", error="Email already exists", status_code=409)

        # Validate role
        role = data.get("role", "commuter")  # Default to commuter
        sacco_name = data.get("sacco_name")

        user = User(name=data["username"], email=data["email"], role=role) # Changed username->name to match User model
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
            
        # Normalize input (though ilike handles the match, cleaning input is good)
        email = email.strip()
        print(f"DEBUG: Searching for driver email: '{email}'")
            
        # Use ilike for case-insensitive DB match
        user = User.query.filter(User.email.ilike(email)).first()
        if not user:
            print(f"DEBUG: Driver not found in DB.")
            return make_response(message="Not Found", error="Driver not found", status_code=404)
        
        print(f"DEBUG: Found user {user.id}, Role: {user.role}, Sacco ID: {user.sacco_id}")
            
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
             
        current_user_id = get_jwt_identity()
        manager = db.session.get(User, current_user_id)
        
        if not manager.sacco_id:
             return make_response(message="Config Error", error="Manager has no Sacco assigned", status_code=500)

        # CHECK: Driver already in another Sacco?
        if user.sacco_id and user.sacco_id != manager.sacco_id:
            # Fetch existing sacco name for better error message if possible, or just generic
            return make_response(message="Conflict", error="Driver is already assigned to another Sacco. Dismiss them first.", status_code=409)

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
        current_user_id = get_jwt_identity()
        manager = db.session.get(User, current_user_id)
        
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
            elif user.sacco_id and user.sacco_id != manager.sacco_id:
                return make_response(message="Conflict", error="Driver is already assigned to another Sacco.", status_code=409)
                
        elif action == "reject":
            user.verification_status = "rejected"
            
        elif action == "dismiss":
            # Release driver from Sacco
            if user.sacco_id == manager.sacco_id:
                user.sacco_id = None
                user.verification_status = "pending" # Reset status
                
                # Also unassign any active vehicle
                for m in user.matatus:
                    if m.assignment_status == 'active':
                        m.assignment_status = 'inactive'
                        m.driver_id = None # Clear driver link if needed, or just status
                        # Actually matatu.driver_id is FK. 
                        # We should set assignment_status to 'history' or just unassign.
                        # Ideally, we set matatu.assignment_status = 'available' (if that's a status)
                        # Let's just set 'inactive' for the link.
                        pass
                
                # If we want to fully free the vehicle:
                # Find the vehicle assigned to this driver
                # Actually user.matatus is the relationship.
                pass
            else:
                return make_response(message="Forbidden", error="Cannot dismiss driver from another Sacco", status_code=403)

        else:
            return make_response(message="Invalid Action", error="Action must be approve, reject, or dismiss", status_code=400)
            
        try:
            db.session.commit()
            return make_response(message=f"Driver {action}d successfully", data=user.to_dict(), status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)


class DriverRouteAssignmentResource(Resource):
    @sacco_manager_required
    def post(self, user_id):
        data = request.get_json() or {}
        route_id = data.get('route_id')
        
        if not route_id:
            return make_response(message="Bad Request", error="Route ID required", status_code=400)
            
        user = db.session.get(User, user_id)
        if not user or user.role != User.ROLE_DRIVER:
            return make_response(message="Not Found", error="Driver not found", status_code=404)
            
        # Find active vehicle for this driver
        # Explicitly joining Matatu to check assignment
        vehicle = next((m for m in user.matatus if m.assignment_status == 'active'), None)
        
        if not vehicle:
            return make_response(message="Conflict", error="Driver has no active vehicle assigned. Assign vehicle first.", status_code=409)
            
        from ..models.route import Route
        from ..models.notification import Notification
        
        route = db.session.get(Route, route_id)
        if not route:
            return make_response(message="Not Found", error="Route not found", status_code=404)
            
        # Assign Route
        vehicle.route_id = route_id
        
        # Create Notification
        manager_identity = get_jwt_identity()
        # manager_name could be fetched, but simple message is fine
        msg = f"You have been assigned to new route: {route.origin} - {route.destination}"
        note = Notification(user_id=user.id, message=msg)
        
        try:
            db.session.add(note)
            db.session.commit()
            return make_response(message="Route assigned successfully", status_code=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status_code=500)

api.add_resource(UserListResource, '/')
api.add_resource(UserResource, '/<int:user_id>')
api.add_resource(RegisterResource, '/register')
api.add_resource(DriverInviteResource, '/manager/invite')
api.add_resource(DriverSearchResource, '/manager/drivers/search')
api.add_resource(DriverActionResource, '/manager/drivers/<int:user_id>/<string:action>')
api.add_resource(DriverRouteAssignmentResource, '/manager/drivers/<int:user_id>/assign-route')
