from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import streamlit as streamlit
import requests
import logging
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / "assets"
TAX_REMINDER_ICON = ASSETS_DIR / "logo" / "icon" / "edgetaxai-icon-color.svg"

from desktop.config import API_BASE_URL

# Configure Logging
logging.basicConfig(
    filename="tax_reminders.log",  # Log file for tax reminders
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def quarterly_tax_reminders_page():
    """
    Quarterly Tax Reminders Page: Schedule SMS reminders for tax payments via API.
    """
    streamlit.title("Quarterly Tax Reminders")
    streamlit.image(str(TAX_REMINDER_ICON), width=50)
    streamlit.markdown("#### Schedule SMS reminders for your quarterly tax payments.")

    # Validate User Session
    if "user_id" not in streamlit.session_state:
        streamlit.error("Please log in to set tax reminders.")
        logging.error("Unauthorized access attempt: User not logged in.")
        return

    user_id = streamlit.session_state["user_id"]

    # Input Fields
    phone_number = streamlit.text_input("Enter Your Phone Number (e.g., +1234567890)")
    reminder_date = streamlit.date_input("Reminder Date")

    if streamlit.button("Schedule Reminder"):
        if not phone_number or not reminder_date:
            streamlit.error("Both phone number and reminder date are required.")
            logging.warning(f"User {user_id} submitted incomplete reminder details.")
        else:
            try:
                payload = {
                    "user_id": user_id,
                    "phone_number": phone_number,
                    "reminder_date": str(reminder_date),
                }
                response = requests.post(f"{API_BASE_URL}/tax/reminders", json=payload)

                if response.status_code == 200:
                    streamlit.success("Reminder scheduled successfully!")
                    logging.info(
                        f"User {user_id} scheduled a reminder for {reminder_date} to {phone_number}."
                    )
                else:
                    error_message = response.json().get(
                        "error", "Failed to schedule reminder."
                    )
                    streamlit.error(error_message)
                    logging.error(
                        f"API Error - Failed to schedule reminder for user {user_id}: {error_message}"
                    )
            except Exception as e:
                streamlit.error(
                    "An unexpected error occurred while scheduling the reminder."
                )
                logging.exception(
                    f"Exception while scheduling reminder for user {user_id}: {e}"
                )
