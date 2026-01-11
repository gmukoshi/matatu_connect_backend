# Matatu Connect Backend

This is the backend for the Matatu Connect application, built with Flask.

## Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual Environment (recommended)

## Setup Instructions

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd matatu_connect_backend
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    This will install all required packages including `flask`, `python-dotenv`, etc.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory (or ensure it exists in `capstone_project`) with the following structure:
    ```ini
    DATABASE_URL=postgresql://postgres:password@localhost:5432/matatu_db
    SECRET_KEY=your_secret_key
    JWT_SECRET_KEY=your_jwt_secret
    # Add other keys as found in capstone_project/app/config.py
    ```

5.  **Run the Application**:
    ```bash
    # Navigate to the project folder if needed, or run from root if configured
    cd capstone_project
    python run.py
    ```
    The server will start on `http://127.0.0.1:5000`.

## Troubleshooting

- **Import Errors**: If you see `ModuleNotFoundError: No module named 'dotenv'`, ensure you have activated your virtual environment and ran `pip install -r requirements.txt`.
