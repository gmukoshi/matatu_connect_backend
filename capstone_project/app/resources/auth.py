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

    user = User(
        name=name,
        email=email,
        role=data.get("role", "commuter")
    )
    user.set_password(password)

    try:
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