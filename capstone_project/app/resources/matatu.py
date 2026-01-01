from flask import Blueprint, jsonify

matatu_bp = Blueprint("matatu", __name__)

@matatu_bp.route("/", methods=["GET"])
def get_matatus():
    return jsonify({"message": "List of matatus"})
