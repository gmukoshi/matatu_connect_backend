from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    return {
        "status": "success",
        "message": message,
        "data": data
    }, status_code

def error_response(message="An error occurred", error=None, status_code=400):
    return {
        "status": "error",
        "message": message,
        "error": error
    }, status_code

# --- ALIASES TO PREVENT IMPORT ERRORS ---
# Satisfies booking.py
api_response = success_response 

# Satisfies matatu.py and route.py
make_response = success_response