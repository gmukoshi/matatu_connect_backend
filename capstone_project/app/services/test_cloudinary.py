from image_service import upload_vehicle_image  # import your function

# Path to a local image file to test
file_path = "test_vehicle.jpg"  # make sure this file exists

# Call the upload function
url = upload_vehicle_image(file_path)

if url:
    print("Upload successful!")
    print("Image URL:", url)
else:
    print("Upload failed.")
