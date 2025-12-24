from app.services.image_service import upload_vehicle_image

file_path = "test_vehicle.jpg"

url = upload_vehicle_image(file_path)

if url:
    print("Upload successful!")
    print("Image URL:", url)
else:
    print("Upload failed.")
