import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_vehicle_image(file_path, folder="matatu_images"):
    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        return result.get("secure_url")
    except Exception as e:
        print("Cloudinary Upload Error:", e)
        return None
