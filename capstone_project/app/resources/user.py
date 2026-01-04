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