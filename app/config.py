import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    
    # Email configuration
    EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "resend")  # "gmail" or "resend"
    
    # Gmail SMTP configuration
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    
    # Resend configuration
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    
    # From email (works for both providers)
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "OpenCredit <noreply@opencredit.co.il>")
    
    # If you have other data with id's that are used in the static data then it will raise an error,
    # so the easy solution is to drop all active data
    ADD_STATIC_OFFERS = True
