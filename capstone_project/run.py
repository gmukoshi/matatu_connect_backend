<<<<<<< HEAD
from app import create_app  # Make sure app/__init__.py has create_app

app = create_app()

if __name__ == "__main__":
    # Run app manually for development
    app.run(debug=True)
=======
from app import create_app  # Make sure app/__init__.py has create_app

app = create_app()

if __name__ == "__main__":
    # Run app manually for development
    app.run(debug=True)
>>>>>>> 234ac08 (moved the init that initializes the app to be a stand alone file,  changed the locations for all the the imports of the connecting to the init since I had changed the location, created a route id column for the foreign key on he route table.)
