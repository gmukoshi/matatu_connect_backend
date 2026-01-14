from app import create_app
from app.extensions import socketio
import os

app = create_app()

if __name__ == '__main__':
    print(">>> SERVER STARTING: VERSION DEBUG_NEW_LOGGING <<<")
    port = int(os.environ.get("PORT", 5000))
    # Local development use
    # debug=True allows for hot-reloading
    # allow_unsafe_werkzeug=True is sometimes needed in newer Flask versions for local dev
    socketio.run(app, host="0.0.0.0", port=port, debug=True)