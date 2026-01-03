from flask import jsonify

def handle_404_error(e):
    """Catch-all for routes that do not exist."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested URL was not found on the server.",
        "status_code": 404
    }), 404

def handle_500_error(e):
    """Catch-all for internal server errors/crashes."""
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred on our end. Please try again later.",
        "status_code": 500
    }), 500

def handle_403_error(e):
    """Catch-all for forbidden access (often triggered by RBAC)."""
    return jsonify({
        "error": "Forbidden",
        "message": "You do not have permission to access this resource.",
        "status_code": 403
    }), 403

def handle_401_error(e):
    """Catch-all for unauthorized access (expired or missing tokens)."""
    return jsonify({
        "error": "Unauthorized",
        "message": "Authentication is required to access this resource.",
        "status_code": 401
    }), 401