from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Matatu Connect! Track vehicles, manage bookings, and ride safely."  


@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.json
    print("Received M-Pesa callback:", data)  # For debugging
    # Here you would normally verify ResultCode, update bookings, etc.
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True)
