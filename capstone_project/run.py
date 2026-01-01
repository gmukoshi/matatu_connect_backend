from flask import Flask, request, jsonify
from config import Config
from app.services.image_service import init_cloudinary, upload_vehicle_image
from app.routes.image_routes import image_bp

app = Flask(__name__)
app.config.from_object(Config)

# 🔹 Initialize Cloudinary HERE
init_cloudinary(app)

# 🔹 Register image upload blueprint
app.register_blueprint(image_bp, url_prefix="/api/images")


@app.route("/")
def home():
    return "Welcome to Matatu Connect! Track vehicles, manage bookings, and ride safely."


@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.json
    print("Received M-Pesa callback:", data)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True)
