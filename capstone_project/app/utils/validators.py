import re
import math
from flask import jsonify

# ==========================
# REGEX PATTERNS
# ==========================
KENYAN_PHONE_REGEX = re.compile(r"^(?:\+254|0)(7|1)\d{8}$")
NUMBER_PLATE_REGEX = re.compile(r"^K[A-Z]{2}\s?\d{3}[A-Z]?$", re.IGNORECASE)
ROUTE_NAME_REGEX = re.compile(r"^[A-Za-z0-9\s\-–toTO]{3,100}$")
STAGE_NAME_REGEX = re.compile(r"^[A-Za-z0-9\s]{2,80}$")

KENYA_LAT_MIN, KENYA_LAT_MAX = -5.0, 5.3
KENYA_LNG_MIN, KENYA_LNG_MAX = 33.5, 42.0


# ==========================
# BASIC VALIDATORS
# ==========================
def validate_phone_number(phone):
    if not phone:
        return None, "Phone number is required"

    phone = phone.replace(" ", "")
    if not KENYAN_PHONE_REGEX.match(phone):
        return None, "Invalid Kenyan phone number"

    if phone.startswith("0"):
        phone = "+254" + phone[1:]

    return phone, None


def validate_number_plate(plate):
    if not plate:
        return None, "Number plate is required"

    plate = plate.strip().upper()
    if not NUMBER_PLATE_REGEX.match(plate):
        return None, "Invalid vehicle number plate"

    return plate, None


def validate_email(email):
    if not email:
        return None, "Email is required"

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return None, "Invalid email"

    return email.lower(), None


def validate_required_fields(data, fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400
    return None


def validate_password(password):
    if not password:
        return None, "Password is required"

    if len(password) < 8:
        return None, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return None, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return None, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return None, "Password must contain at least one number"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return None, "Password must contain at least one special character"

    return password, None


# ==========================
# ROUTES & STAGES
# ==========================
def validate_route_name(name):
    if not name:
        return None, "Route name required"

    name = name.strip().title()
    if not ROUTE_NAME_REGEX.match(name):
        return None, "Invalid route name"

    return name, None


def validate_stage_name(name):
    if not name:
        return None, "Stage name required"

    name = name.strip().title()
    if not STAGE_NAME_REGEX.match(name):
        return None, "Invalid stage name"

    return name, None


# ==========================
# GPS + DISTANCE
# ==========================
def validate_coordinates(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None, "Coordinates must be numbers"

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, "Invalid coordinate range"

    if not (KENYA_LAT_MIN <= lat <= KENYA_LAT_MAX and
            KENYA_LNG_MIN <= lng <= KENYA_LNG_MAX):
        return None, "Coordinates outside Kenya"

    return {"lat": lat, "lng": lng}, None


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    phi1, phi2 = map(math.radians, [lat1, lat2])
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 3)


def calculate_route_length(stages):
    distance = 0
    for i in range(len(stages) - 1):
        distance += haversine(
            stages[i]["lat"], stages[i]["lng"],
            stages[i+1]["lat"], stages[i+1]["lng"]
        )
    return round(distance, 2)


def snap_to_nearest_road(lat, lng):
    # Safe stub (replace with OSRM / Google Roads later)
    return {"lat": lat, "lng": lng}

# ==========================
# GEO HELPERS (ADVANCED)
# ==========================

def distance_to_point(lat1, lng1, lat2, lng2):
    """
    Distance between current location and a stage (KM)
    """
    return haversine(lat1, lng1, lat2, lng2)


def is_arrived_at_stage(
    current_lat,
    current_lng,
    stage_lat,
    stage_lng,
    threshold_meters=50
):
    """
    Detect arrival within X meters of a stage
    Default: 50 meters (urban accuracy)
    """
    distance_km = distance_to_point(
        current_lat, current_lng, stage_lat, stage_lng
    )

    return (distance_km * 1000) <= threshold_meters


def estimate_eta(distance_km, speed_kmh):
    """
    Estimate ETA in minutes
    """
    if speed_kmh <= 0:
        return None

    hours = distance_km / speed_kmh
    return round(hours * 60, 1)


def traffic_delay_multiplier(speed_kmh):
    """
    Simple traffic model (no external API)
    """
    if speed_kmh >= 40:
        return 1.0      # Free flow
    if speed_kmh >= 20:
        return 1.3      # Moderate traffic
    return 1.6          # Heavy traffic

