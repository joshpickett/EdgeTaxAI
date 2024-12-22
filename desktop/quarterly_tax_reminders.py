import streamlit as st
import requests
import logging
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
TAX_REMINDER_ICON = ASSETS_DIR / 'logo' / 'icon' / 'edgetaxai-icon-color.svg'

from config import API_BASE_URL

# Configure Logging
logging.basicConfig(
    filename="tax_reminders.log",  # Log file for tax reminders
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def quarterly_tax_reminders_page():
    """
    Quarterly Tax Reminders Page: Schedule SMS reminders for tax payments via API.
    """
    st.title("Quarterly Tax Reminders")
    st.image(str(TAX_REMINDER_ICON), width=50)
    st.markdown("#### Schedule SMS reminders for your quarterly tax payments.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to set tax reminders.")
        logging.error("Unauthorized access attempt: User not logged in.")
        return

    user_id = st.session_state["user_id"]

    # Input Fields
    phone_number = st.text_input("Enter Your Phone Number (e.g., +1234567890)")
    reminder_date = st.date_input("Reminder Date")

    if st.button("Schedule Reminder"):
        if not phone_number or not reminder_date:
            st.error("Both phone number and reminder date are required.")
            logging.warning(f"User {user_id} submitted incomplete reminder details.")
        else:
            try:
                payload = {
                    "user_id": user_id,
                    "phone_number": phone_number,
                    "reminder_date": str(reminder_date)
                }
                response = requests.post(f"{API_BASE_URL}/tax/reminders", json=payload)

                if response.status_code == 200:
                    st.success("Reminder scheduled successfully!")
                    logging.info(f"User {user_id} scheduled a reminder for {reminder_date} to {phone_number}.")
                else:
                    error_message = response.json().get("error", "Failed to schedule reminder.")
                    st.error(error_message)
                    logging.error(f"API Error - Failed to schedule reminder for user {user_id}: {error_message}")
            except Exception as e:
                st.error("An unexpected error occurred while scheduling the reminder.")
                logging.exception(f"Exception while scheduling reminder for user {user_id}: {e}")
