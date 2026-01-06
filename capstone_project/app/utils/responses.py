from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """
    Standard format for successful API responses.
    """
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status_code

def error_response(message="An error occurred", error=None, status_code=400):
    """
    Standard format for error API responses.
    """
    return jsonify({
        "status": "error",
        "message": message,
        "error": error
    }), status_code

def make_response(data=None, message="Success", error=None, status_code=200):
    """
    A smart wrapper that decides whether to return a success or error 
    response based on the provided status code.
    Used by matatu.py and route.py.
    """
    if status_code >= 400:
        return error_response(message=message, error=error, status_code=status_code)
    return success_response(data=data, message=message, status_code=status_code)

# --- Aliases for backward compatibility with different resource files ---

# Satisfies booking.py
api_response = success_response

# Ensures that any resource expecting a generic response handler works
send_response = make_response