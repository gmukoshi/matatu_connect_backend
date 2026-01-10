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

# SACCO MANAGER ONLY: View drivers in their Sacco
@user_bp.route('/manager/drivers', methods=['GET'])
@sacco_manager_required
def get_sacco_drivers():
    drivers = User.query.filter_by(role=User.ROLE_DRIVER).all()
    return jsonify([d.to_dict() for d in drivers]), 200

from flask import request
from flask_restful import Resource
from ..models.user import User
from ..extensions import db
from ..utils.responses import make_response

class UserListResource(Resource):
    # Optional: admin only
    def get(self):
        users = User.query.all()
        return make_response(
            message="Users fetched successfully",
            data=[u.to_dict() for u in users],
            status=200
        )

class UserResource(Resource):
    # Optional: public profile or admin fetch
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status=404)
        return make_response(message="User fetched successfully", data=user.to_dict(), status=200)

    # Optional: admin delete
    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status=404)

        try:
            db.session.delete(user)
            db.session.commit()
            return make_response(message="User deleted successfully", status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)

class RegisterResource(Resource):
    def post(self):
        data = request.get_json() or {}
        required = ("username", "email", "password")
        if not all(k in data for k in required):
            return make_response(
                message="Validation Error",
                error="Missing fields: username, email, password",
                status=400
            )

        if User.query.filter_by(email=data["email"]).first():
            return make_response(message="Conflict", error="Email already exists", status=409)

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])  # you must implement set_password in model

        try:
            db.session.add(user)
            db.session.commit()
            return make_response(message="User registered successfully", data=user.to_dict(), status=201)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)

