import os
from dotenv import load_dotenv

# Load environment variables from a `.env` file
load_dotenv()

# ---- General Flask Configuration ----
class Config:
    APP_NAME = "TaxEdgeAI Backend"
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"  # Enable Flask debug mode
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Flask session encryption key

    # ---- Logging Configuration ----
    LOG_FILE = os.getenv("LOG_FILE", "api.log")  # Log file location
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Logging level (DEBUG, INFO, ERROR)

    # ---- Database Configuration ----
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Default SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- API Keys ----
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET = os.getenv("PLAID_SECRET", "")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # ---- IRS Configuration ----
    IRS_MILEAGE_RATE = float(os.getenv("IRS_MILEAGE_RATE", "0.655"))  # Default IRS mileage rate

    # ---- CORS (Cross-Origin Resource Sharing) ----
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")  # Adjust for production to specific domains
