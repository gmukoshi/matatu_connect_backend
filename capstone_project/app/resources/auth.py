from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from ..extensions import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name") # Required by your User model

    if not email or not password or not name:
        return {"error": "name, email and password are required"}, 400
    
    if User.query.filter_by(email=email).first():
        return {"error": "Email already registered"}, 409

    
    # Handle specific fields for driver role
    license_number = data.get("licence") if data.get("role") == "driver" else None
    
    user = User(
        name=name,
        email=email,
        role=data.get("role", "commuter"),
        license_number=license_number,
        verification_status="pending" if data.get("role") == "driver" else "approved",
        sacco_id=data.get("sacco_id") # Assign selected Sacco
    )

    user.set_password(password)

    try:
        # Check if new Sacco creation is requested
        sacco_name = data.get("sacco_name")
        if not user.sacco_id and sacco_name and user.role == "sacco_manager":
            from ..models.sacco import Sacco
            # Check if name exists to prevent duplicates via name-entry
            existing_sacco = Sacco.query.filter_by(name=sacco_name).first()
            if existing_sacco:
                user.sacco_id = existing_sacco.id
            else:
                new_sacco = Sacco(name=sacco_name)
                db.session.add(new_sacco)
                db.session.flush() # Get ID
                user.sacco_id = new_sacco.id

        db.session.add(user)
        db.session.commit()
        
        # Auto-login: Generate tokens
        identity = {"id": user.id, "role": user.role}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return {
            "message": "User registered successfully",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        # Note: Frontend sends 'email' key even if value is username
        return {"error": "Missing credentials"}, 400

    # Allow login by email OR name (username/sacco name)
    login_identifier = data["email"]
    user = User.query.filter((User.email == login_identifier) | (User.name == login_identifier)).first()
    
    if not user or not user.check_password(data["password"]):
        return {"error": "Invalid credentials"}, 401

    identity = {"id": user.id, "role": user.role}

    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": user.to_dict()
    }, 200