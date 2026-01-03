import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================
    # JWT CONFIG
    # ======================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    # ======================
    # SENDGRID EMAIL CONFIG
    # ======================
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "no-reply@matatuconnect.com"
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False

