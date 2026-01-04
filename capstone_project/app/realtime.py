from flask_socketio import emit, join_room, leave_room
from .extensions import socketio

@socketio.on("connect")
def on_connect():
    emit("server:connected", {"message": "connected"})

@socketio.on("disconnect")
def on_disconnect():
    # optional logging
    pass

@socketio.on("room:join")
def on_join(data):
    room = data.get("room")
    if room:
        join_room(room)
        emit("room:joined", {"room": room})

@socketio.on("room:leave")
def on_leave(data):
    room = data.get("room")
    if room:
        leave_room(room)
        emit("room:left", {"room": room})

def broadcast_route_update(route_id: int, payload: dict):
    """
    Call this from your REST endpoints or background jobs
    to push updates to subscribers.
    """
    socketio.emit("route:update", payload, room=f"route:{route_id}")
