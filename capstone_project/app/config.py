import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    """Base configuration common to all environments."""
    
    # --- Core Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this")
    
    # --- Database (PostgreSQL) ---
    # Defaulting to local postgres if DATABASE_URL is not found in .env
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/matatu_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT Security ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"] # Explicitly look in headers (Bearer <token>)
    JWT_ERROR_MESSAGE_KEY = "message" 

    # --- M-PESA DARAJA API (Fintech Integration) ---
    # Get these from https://developer.safaricom.co.ke/
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "8xoAQBO7BIGkEx8GERN2TetmhjECMs9QirSzQqFzh32oR9zu")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "Q2WFZMo1Okt0QuAjv8MzDFgxwbYROqLV1Xm5TGyknd33dP4eS42Zp9qorYGuUI3B")
    
    # Environment: 'sandbox' or 'production'
    MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")
    
    # Base URL switching
    if MPESA_ENV == "production":
        MPESA_API_BASE_URL = "https://api.safaricom.co.ke"
    else:
        MPESA_API_BASE_URL = "https://sandbox.safaricom.co.ke"

    # Default Sandbox Shortcode is 174379
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
    
    # Passkey for Lipa Na M-Pesa Online (STK Push)
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
    
    # The URL Safaricom will send payment results to
    # Switched to Render URL by default to ensure stability without Ngrok
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://matatu-connect-backend-l7lb.onrender.com/api/payments/callback")

    # --- Email Service (SendGrid) ---
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@matatuconnect.com")

    # --- Frontend Integration ---
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

class DevelopmentConfig(Config):
    DEBUG = True
    # Allows for testing M-Pesa callbacks locally if using a tool like Ngrok
    DEBUG_TB_INTERCEPT_REDIRECTS = False 

class ProductionConfig(Config):
    DEBUG = False
    # Use stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PROPAGATE_EXCEPTIONS = True
    # In production, ensure the DATABASE_URL uses 'postgresql://' instead of 'postgres://'
    # (Heroku and some providers often use the 'postgres' prefix which SQLAlchemy 1.4+ dislikes)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    DEBUG = True

# Helper to map environment names to classes
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}