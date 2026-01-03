from flask import jsonify

def api_response(message, data=None, status="success", status_code=200):
    """Standardized JSON response format for all API endpoints."""
    response = {
        "status": status,
        "message": message,
        "data": data
    }
    return response, status_code