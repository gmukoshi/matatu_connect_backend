import cloudinary
import cloudinary.uploader

def init_cloudinary(app):
    """
    Initialize Cloudinary with credentials from app config.
    """
    cloudinary.config(
        cloud_name=app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=app.config.get("CLOUDINARY_API_KEY"),
        api_secret=app.config.get("CLOUDINARY_API_SECRET")
    )

def upload_vehicle_image(file, folder="matatu_images"):
    """
    Upload a file to Cloudinary and return the secure URL.
    Accepts a file object (from Flask request.files).
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder
        )
        return result.get("secure_url")
    except Exception as e:
        print("Cloudinary upload failed:", e)
        return None
