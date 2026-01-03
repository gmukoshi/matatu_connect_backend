from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json()

    user = User(
        email=data["email"],
        role=data.get("role", "commuter")  # default role
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return {"error": "Invalid credentials"}, 401

    identity = {
        "id": user.id,
        "role": user.role
    }

    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity)
    }, 200
