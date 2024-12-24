import streamlit as streamlit
import platform
from datetime import datetime, timedelta
from pathlib import Path
import logging
import keyring
from shared.services.authService import AuthService
from shared.constants import AUTH_STATES, ERROR_TYPES
from utils import validate_input_fields

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
LOGO = ASSETS_DIR / 'logo' / 'primary' / 'edgetaxai-horizontal-color.svg'

auth_service = AuthService()

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
            streamlit.warning("Session expired. Please log in again")

    def handle_login(identifier: str, otp: str) -> bool:
        try:
            response = auth_service.login({ 'identifier': identifier, 'otp': otp })
            if response.token:
                streamlit.session_state.authenticated = True
                streamlit.session_state.session_expiry = datetime.now() + timedelta(hours=24)
                return True
            return False
        except Exception as e:
            streamlit.error(f"Login failed: {str(e)}")
            return False

    if not streamlit.session_state.otp_sent:
        if streamlit.button("Send OTP"):
            handle_send_otp()
            
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
                return True
