from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.services.email_service import send_welcome_email
from app.models.user import User
from app.extensions import db


# ==========================
# Role constants
# ==========================
ROLE_COMMUTER = "commuter"
ROLE_DRIVER = "driver"
ROLE_SACCO_MANAGER = "sacco_manager"
ROLE_ADMIN = "admin"


# ==========================
# RBAC DECORATORS
# ==========================
def roles_required(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            if not identity or "role" not in identity:
                return jsonify({"error": "Invalid token"}), 401

            if identity["role"] not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403

            return fn(*args, **kwargs)

        return decorator
    return wrapper


commuter_required = roles_required(ROLE_COMMUTER)
driver_required = roles_required(ROLE_DRIVER)
sacco_manager_required = roles_required(ROLE_SACCO_MANAGER)
admin_required = roles_required(ROLE_ADMIN)

staff_required = roles_required(
    ROLE_DRIVER, ROLE_SACCO_MANAGER, ROLE_ADMIN
)

any_authenticated_user = roles_required(
    ROLE_COMMUTER, ROLE_DRIVER, ROLE_SACCO_MANAGER, ROLE_ADMIN
)


# ==========================
# AUTH SERVICE LOGIC
# ==========================
def register_user(name, email, password, role=ROLE_COMMUTER):
    """
    Handles user registration and sends welcome email
    """
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None, "User already exists"

    user = User(
        name=name,
        email=email,
        role=role,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Send welcome email (non-blocking)
    send_welcome_email(user.email, user.name)

    return user, None
