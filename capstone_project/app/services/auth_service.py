from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

# ...

# ==========================
# RBAC DECORATORS
# ==========================
def roles_required(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Identity is now just the user ID string, so we check claims for role
            if not claims or "role" not in claims:
                return jsonify({"error": "Invalid token claims (missing role)"}), 401

            if claims["role"] not in allowed_roles:
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
