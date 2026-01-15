from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from ..extensions import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").lower().strip() # Normalize email
    password = data.get("password")
    name = data.get("name") # Required by your User model

    if not email or not password or not name:
        return {"error": "name, email and password are required"}, 400
    
    if data.get("role") == "driver" and not data.get("licence"):
         return {"error": "License number is required for drivers"}, 400
    
    if User.query.filter_by(email=email).first():
        return {"error": "Email already registered"}, 409

    
    # Handle specific fields for driver role
    license_number = data.get("licence") if data.get("role") == "driver" else None
    
    user = User(
        name=name,
        email=email,
        phone_number=data.get("phone_number"), # Added missing field
        role=data.get("role", "commuter"),
        license_number=license_number,
        verification_status=data.get("verification_status", "pending" if data.get("role") == "driver" else "approved"),
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
        # Identity MUST be a string (User ID)
        identity = str(user.id)
        claims = {"role": user.role, "sacco_id": user.sacco_id}
        
        access_token = create_access_token(identity=identity, additional_claims=claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=claims)
        
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

    # Allow login by email (normalized) OR name (username/sacco name)
    login_input = data.get("email", "").strip() 
    password = data.get("password")

    # Try email first (lowercased)
    user = User.query.filter_by(email=login_input.lower()).first()
    
    if not user:
        # Fallback to name match (exact case or depends on DB collation)
        user = User.query.filter_by(name=login_input).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid credentials"}, 401

    identity = str(user.id)
    claims = {"role": user.role, "sacco_id": user.sacco_id}

    access_token = create_access_token(identity=identity, additional_claims=claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=claims)

    return {
        "message": "Login successful",
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }, 200