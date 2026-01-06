import math
from datetime import datetime
from flask_socketio import emit
from ..extensions import db, socketio
from ..models.matatu import Matatu

# ------------------------
# Distance calculation
# ------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ------------------------
# ETA calculation
# ------------------------
def calculate_eta(distance_km, avg_speed_kmh=30, traffic_factor=1.0):
    """
    traffic_factor >1 means traffic delay
    """
    if avg_speed_kmh <= 0:
        return None
    hours = (distance_km / avg_speed_kmh) * traffic_factor
    return round(hours * 60)  # minutes


# ------------------------
# Arrival detection
# ------------------------
def has_arrived(current_lat, current_lng, stage_lat, stage_lng, threshold_m=50):
    distance = haversine(current_lat, current_lng, stage_lat, stage_lng)
    return distance * 1000 <= threshold_m


# ------------------------
# Live GPS update
# ------------------------
def update_matatu_location(matatu_id, latitude, longitude):
    matatu = Matatu.query.get(matatu_id)
    if not matatu:
        return

    matatu.latitude = latitude
    matatu.longitude = longitude
    matatu.last_updated = datetime.utcnow()
    db.session.commit()

    socketio.emit(
        "gps_update",
        {
            "matatu_id": matatu.id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": matatu.last_updated.isoformat()
        },
        namespace="/realtime"
    )
