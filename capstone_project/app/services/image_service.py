import cloudinary
from cloudinary import uploader
import os

def init_cloudinary(app=None):
    """
    Initialize Cloudinary using either app config or environment variables.
    """
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME") or app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY") or app.config.get("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET") or app.config.get("CLOUDINARY_API_SECRET")
    )

def upload_vehicle_image(file, folder="matatu_images"):
    """
    Upload a file to Cloudinary and return the secure URL.
    Accepts a file object (from Flask request.files).
    """
    try:
        result = uploader.upload(file, folder=folder)
        return result.get("secure_url")  # Always returns HTTPS URL
    except Exception as e:
        print("Cloudinary upload failed:", e)
        return None
