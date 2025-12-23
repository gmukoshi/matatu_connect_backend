from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Matatu Connect! Track vehicles, manage bookings, and ride safely."  # project-specific message

if __name__ == "__main__":
    app.run(debug=True)
