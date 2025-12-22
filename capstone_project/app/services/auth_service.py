from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify

# Role constants (single source of truth)
ROLE_COMMUTER = "commuter"
ROLE_DRIVER = "driver"
ROLE_SACCO_MANAGER = "sacco_manager"
ROLE_ADMIN = "admin"


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


# Single-role decorators
commuter_required = roles_required(ROLE_COMMUTER)
driver_required = roles_required(ROLE_DRIVER)
sacco_manager_required = roles_required(ROLE_SACCO_MANAGER)
admin_required = roles_required(ROLE_ADMIN)

# Multi-role decorators
staff_required = roles_required(
    ROLE_DRIVER, ROLE_SACCO_MANAGER, ROLE_ADMIN
)

any_authenticated_user = roles_required(
    ROLE_COMMUTER, ROLE_DRIVER, ROLE_SACCO_MANAGER, ROLE_ADMIN
)
