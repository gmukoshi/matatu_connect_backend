from flask import Flask
from .services.image_service import init_cloudinary

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Initialize Cloudinary
    init_cloudinary(app)

    return app
