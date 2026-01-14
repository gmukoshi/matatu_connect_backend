
from app import create_app
from app.extensions import db
from sqlalchemy import text  # Import for raw SQL execution

app = create_app()

def add_reply_column():
    with app.app_context():
        try:
            # Using raw SQL to alter table
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE ratings ADD COLUMN reply TEXT;"))
                conn.commit()
            print("Successfully added 'reply' column to 'ratings' table.")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("Column 'reply' already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_reply_column()
