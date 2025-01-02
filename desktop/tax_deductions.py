from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import streamlit as streamlit
import requests
import pandas as pd
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / "assets"
DEDUCTION_ICON = ASSETS_DIR / "logo" / "icon" / "edgetaxai-icon-color.svg"

from desktop.config import API_BASE_URL


def tax_deductions_page():
    """
    Tax Deductions Page: Fetch and display flagged tax-deductible expenses via API.
    Users can upload or input custom expenses for AI deduction suggestions.
    """
    streamlit.title("AI-Flagged Tax Deductions")
    streamlit.image(str(DEDUCTION_ICON), width=50)
    streamlit.markdown("#### Optimize your expenses with AI-detected deductions.")

    # Validate User Session
    if "user_id" not in streamlit.session_state:
        streamlit.error("Please log in to view tax deductions.")
        return

    user_id = streamlit.session_state["user_id"]

    # Input Custom Expenses
    streamlit.subheader("Upload or Input Expenses for Deduction Suggestions")
    uploaded_file = streamlit.file_uploader(
        "Upload a CSV file with 'description' and 'amount' columns", type=["csv"]
    )

    if uploaded_file:
        expenses_df = pd.read_csv(uploaded_file)
    else:
        streamlit.info("Alternatively, manually input expenses below:")
        description = streamlit.text_input("Expense Description")
        amount = streamlit.number_input("Expense Amount", min_value=0.0, step=0.01)

        # Create a DataFrame for manual input
        expenses_df = pd.DataFrame()
        if description and amount:
            expenses_df = pd.DataFrame([{"description": description, "amount": amount}])

    if not expenses_df.empty:
        streamlit.info("Fetching AI-based deduction suggestions...")
        try:
            # Convert expenses to JSON format
            expenses = expenses_df.to_dict(orient="records")
            response = requests.post(
                f"{API_BASE_URL}/tax/deductions", json={"expenses": expenses}
            )

            if response.status_code == 200:
                suggestions = response.json().get("suggestions", [])
                if suggestions:
                    suggestions_df = pd.DataFrame(suggestions)
                    streamlit.subheader("Flagged Tax-Deductible Expenses")
                    streamlit.dataframe(suggestions_df)
                else:
                    streamlit.info("No tax-deductible expenses detected.")
            else:
                streamlit.error(
                    response.json().get(
                        "error", "Failed to fetch deduction suggestions."
                    )
                )
        except Exception as e:
            streamlit.error(f"An error occurred while fetching tax deductions: {e}")
    else:
        streamlit.info("Upload or input expenses to see AI deduction suggestions.")
