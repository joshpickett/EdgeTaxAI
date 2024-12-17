import streamlit as st
import requests
import pandas as pd
from config import API_BASE_URL

def tax_deductions_page():
    """
    Tax Deductions Page: Fetch and display flagged tax-deductible expenses via API.
    """
    st.title("AI-Flagged Tax Deductions")
    st.markdown("#### Optimize your expenses with AI-detected deductions.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to view tax deductions.")
        return

    user_id = st.session_state["user_id"]

    # Fetch tax-deductible expenses
    try:
        st.info("Fetching your flagged tax deductions...")
        response = requests.get(f"{API_BASE_URL}/tax/deductions/{user_id}")

        if response.status_code == 200:
            deductions = response.json().get("deductions", [])
            if deductions:
                df = pd.DataFrame(deductions)
                st.subheader("Flagged Tax-Deductible Expenses")
                st.dataframe(df)
            else:
                st.info("No tax-deductible expenses found.")
        else:
            st.error(response.json().get("error", "Failed to fetch tax deductions."))
    except Exception as e:
        st.error(f"An error occurred while fetching tax deductions: {e}")
