# app/sockets/events.py
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app.extensions import socketio, db
from app.utils.validators import validate_gps_coordinates
from datetime import datetime
from app.models.matatu import Matatu

# ===============================
# CONNECTION EVENTS
# ===============================

@socketio.on("connect")
def handle_connect():
    print("🟢 Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("🔴Client disconnected")


# ----------------------------------
# JOIN ROUTE (COMMUTERS)
# ----------------------------------
@socketio.on("join_route")
def join_route(data):
    """
    data = { "route_id": 3 }
    """
    route_id = data.get("route_id")
    room = f"route_{route_id}"

    join_room(room)

    emit(
        "joined_route",
        {"message": f"Joined route {route_id}"},
        room=room
    )


# ----------------------------------
# JOIN MATATU (ADMIN / DRIVER)
# ----------------------------------
@socketio.on("join_matatu")
def join_matatu(data):
    """
    data = { "matatu_id": 12 }
    """
    matatu_id = data.get("matatu_id")
    room = f"matatu_{matatu_id}"

    join_room(room)

    emit(
        "joined_matatu",
        {"message": f"Tracking matatu {matatu_id}"},
        room=room
    )


# ----------------------------------
# DRIVER GPS UPDATE
# ----------------------------------
@socketio.on("location_update")
def handle_location_update(data):
    """
    data = {
        "matatu_id": 12,
        "route_id": 3,
        "latitude": -1.286389,
        "longitude": 36.817223,
        "speed": 45
    }
    """

    matatu_id = data.get("matatu_id")
    route_id = data.get("route_id")

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    speed = data.get("speed", 0)

    if not all([matatu_id, route_id, latitude, longitude]):
        return

    # ----------------------------
    # Save last known position
    # ----------------------------
    matatu = Matatu.query.get(matatu_id)
    if matatu:
        matatu.latitude = latitude
        matatu.longitude = longitude
        matatu.last_updated = datetime.utcnow()
        db.session.commit()

    payload = {
        "matatu_id": matatu_id,
        "route_id": route_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "timestamp": datetime.utcnow().isoformat()
    }

    # ----------------------------
    # Broadcast to commuters
    # ----------------------------
    socketio.emit(
        "matatu_location_update",
        payload,
        room=f"route_{route_id}"
    )

    # ----------------------------
    # Broadcast to matatu room
    # ----------------------------
    socketio.emit(
        "matatu_location_update",
        payload,
        room=f"matatu_{matatu_id}"
    )
