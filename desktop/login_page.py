import streamlit as streamlit
import requests
import platform
from pathlib import Path
import logging
import keyring
from utils import validate_input_fields, send_post_request
from datetime import datetime, timedelta

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
LOGO = ASSETS_DIR / 'logo' / 'primary' / 'edgetaxai-horizontal-color.svg'

def login_page(api_base_url: str):
    streamlit.title("Login")
    streamlit.image(str(LOGO), width=200)

    # State management
    if 'otp_sent' not in streamlit.session_state:
        streamlit.session_state.otp_sent = False
        streamlit.session_state.authenticated = False

    # Add session expiry check
    if 'session_expiry' in streamlit.session_state:
        if datetime.now() > streamlit.session_state.session_expiry:
            streamlit.session_state.clear()
            streamlit.warning("Session expired. Please log in again.")

    # Check if biometric authentication is available
    biometric_available = False
    if platform.system() in ['Darwin', 'Windows']:  # macOS or Windows
        try:
            biometric_available = True
        except Exception:
            pass

    def handle_send_otp():
        # Logic to send OTP
        pass

    def handle_login(identifier, otp):
        try:
            response = requests.post(
                f"{api_base_url}/auth/login",
                json={"identifier": identifier, "otp": otp}
            )
            return response.status_code == 200
        except Exception as e:
            streamlit.error(f"Login failed: {str(e)}")
            return False

    def handle_biometric_login():
        try:
            # Attempt to get stored credentials
            stored_token = keyring.get_password("taxedgeai", "login_token")
            if stored_token:
                response = requests.post(
                    f"{api_base_url}/auth/biometric/verify",
                    json={"token": stored_token}
                )
                return response.status_code == 200
            return False
        except Exception as e:
            streamlit.error(f"Biometric authentication failed: {str(e)}")
            return False

    if not streamlit.session_state.otp_sent:
        if streamlit.button("Send OTP"):
            handle_send_otp()
            
        # Show biometric option if available
        if biometric_available:
            if streamlit.button("Login with Biometrics"):
                if handle_biometric_login():
                    streamlit.success("Login successful!")
                    streamlit.session_state.authenticated = True
                    streamlit.session_state.session_expiry = datetime.now() + timedelta(hours=24)
                    return True

    # Input fields with validation
    identifier = streamlit.text_input("Identifier (Email or Phone)")
    otp = streamlit.text_input("OTP")

    # Add remember me checkbox
    remember_me = streamlit.checkbox("Remember me on this device")
    
    if remember_me:
        try:
            keyring.set_password("taxedgeai", "last_login", identifier)
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")

    # OTP verification form
    if streamlit.session_state.otp_sent:
        if streamlit.button("Login"):
            if handle_login(identifier, otp):
                streamlit.success("Login successful!")
                streamlit.session_state.authenticated = True
                streamlit.session_state.session_expiry = datetime.now() + timedelta(hours=24)
                return True
