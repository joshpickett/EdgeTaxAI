import streamlit as st
import requests
import logging
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / "assets"
PLAID_ICON = ASSETS_DIR / "logo" / "icon" / "edgetaxai-icon-color.svg"

from config import API_BASE_URL


def plaid_integration_page():
    st.title("Plaid Integration")
    st.image(str(PLAID_ICON), width=50)
    st.markdown("#### Connect your bank accounts securely.")
