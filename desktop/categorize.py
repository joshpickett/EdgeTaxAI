from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import requests
import logging
import streamlit as streamlit


def categorize_expense(api_base_url, description):
    """
    Send expense description to the API for AI-based categorization.
    """
    if not description:
        return "Invalid_Input"

    try:
        payload = {"description": description}
        response = requests.post(f"{api_base_url}/expenses/categorize", json=payload)

        if response.status_code == 200:
            return response.json().get("category", "Uncategorized")
        else:
            return "Uncategorized"
    except Exception as e:
        logging.error(f"Error categorizing expense: {e}")
        return "Error"
