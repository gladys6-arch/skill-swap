import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///skillhub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = False

    # ==========================
    # M-PESA CONFIGURATION
    # ==========================
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY') or 'your_sandbox_consumer_key'
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET') or 'your_sandbox_consumer_secret'
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE') or '174379'  # Default test shortcode
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY') or 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    MPESA_BASE_URL = os.environ.get('MPESA_BASE_URL') or 'https://sandbox.safaricom.co.ke'
