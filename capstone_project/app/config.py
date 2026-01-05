import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration common to all environments."""
    # Core Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this")
    
    # Database - Defaulting to PostgreSQL for your Matatu Project
    # Format: postgresql://user:password@localhost:5432/dbname
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/matatu_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2) # Increased for easier development
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # Prevent JWT errors during development
    JWT_ERROR_MESSAGE_KEY = "message" 

    # Email Service (SendGrid)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "no-reply@matatuconnect.com"
    )

class DevelopmentConfig(Config):
    DEBUG = True
    # You can override specific dev settings here

class ProductionConfig(Config):
    DEBUG = False
    # Use stricter security in production
    SESSION_COOKIE_SECURE = True
    PROPAGATE_EXCEPTIONS = True

# Helper to map environment names to classes
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}