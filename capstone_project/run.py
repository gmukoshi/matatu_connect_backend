from app import create_app  # Make sure app/__init__.py has create_app

app = create_app()

if __name__ == "__main__":
    # Run app manually for development
    app.run(debug=True)
