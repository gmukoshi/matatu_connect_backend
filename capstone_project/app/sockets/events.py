# app/sockets/events.py
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app.extensions import socketio
from app.utils.validators import validate_gps_coordinates
from datetime import datetime

# ===============================
# CONNECTION EVENTS
# ===============================

@socketio.on("connect")
def handle_connect():
    print("🔌 Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")


# ===============================
# ROOM MANAGEMENT
# ===============================

@socketio.on("join_route")
def handle_join_route(data):
    """
    Commuter joins a route room to receive live updates
    """
    route_id = data.get("route_id")
    if not route_id:
        return

    room = f"route_{route_id}"
    join_room(room)

    emit("joined_route", {
        "route_id": route_id,
        "message": "Subscribed to live route updates"
    })


@socketio.on("leave_route")
def handle_leave_route(data):
    route_id = data.get("route_id")
    if not route_id:
        return

    room = f"route_{route_id}"
    leave_room(room)

    emit("left_route", {"route_id": route_id})


# ===============================
# GPS LOCATION UPDATE (DRIVER)
# ===============================

@socketio.on("driver_location_update")
def handle_driver_location_update(data):
    """
    Receives live GPS from driver app and broadcasts to commuters
    """

    route_id = data.get("route_id")
    lat = data.get("latitude")
    lng = data.get("longitude")
    speed = data.get("speed", 0)

    if not route_id:
        emit("error", {"message": "route_id required"})
        return

    # Validate GPS
    if not validate_gps_coordinates(lat, lng):
        emit("error", {"message": "Invalid GPS coordinates"})
        return

    payload = {
        "route_id": route_id,
        "latitude": lat,
        "longitude": lng,
        "speed": speed,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Broadcast to all commuters on this route
    room = f"route_{route_id}"
    emit("route_location_update", payload, room=room)

    # Optional ACK to driver
    emit("location_received", {"status": "ok"})
