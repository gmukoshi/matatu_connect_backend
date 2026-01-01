from flask import Blueprint, request, jsonify
from app.services.image_service import upload_vehicle_image  # 👈 NEW

matatu_bp = Blueprint("matatu", __name__)

@matatu_bp.route("/", methods=["GET"])
def get_matatus():
    return jsonify({"message": "List of matatus"})


@matatu_bp.route("/upload-test", methods=["POST"])
def upload_test():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    url = upload_vehicle_image(file)

    if url:
        return jsonify({"url": url}), 200
    else:
        return jsonify({"error": "Upload failed"}), 500
