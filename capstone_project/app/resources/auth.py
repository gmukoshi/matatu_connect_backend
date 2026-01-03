from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from ..extensions import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "email and password are required"}, 400

    user = User(
        email=email,
        role=data.get("role", "commuter")
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "email and password are required"}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {"error": "Invalid credentials"}, 401

    identity = {"id": user.id, "role": user.role}

    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity)
    }, 200
