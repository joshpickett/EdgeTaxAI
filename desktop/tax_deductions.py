import streamlit as st
import requests
import pandas as pd
from config import API_BASE_URL

def tax_deductions_page():
    """
    Tax Deductions Page: Fetch and display flagged tax-deductible expenses via API.
    Users can upload or input custom expenses for AI deduction suggestions.
    """
    st.title("AI-Flagged Tax Deductions")
    st.markdown("#### Optimize your expenses with AI-detected deductions.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to view tax deductions.")
        return

    user_id = st.session_state["user_id"]

    # Input Custom Expenses
    st.subheader("Upload or Input Expenses for Deduction Suggestions")
    uploaded_file = st.file_uploader("Upload a CSV file with 'description' and 'amount' columns", type=["csv"])

    if uploaded_file:
        expenses_df = pd.read_csv(uploaded_file)
    else:
        st.info("Alternatively, manually input expenses below:")
        description = st.text_input("Expense Description")
        amount = st.number_input("Expense Amount", min_value=0.0, step=0.01)

        # Create a DataFrame for manual input
        expenses_df = pd.DataFrame()
        if description and amount:
            expenses_df = pd.DataFrame([{"description": description, "amount": amount}])

    if not expenses_df.empty:
        st.info("Fetching AI-based deduction suggestions...")
        try:
            # Convert expenses to JSON format
            expenses = expenses_df.to_dict(orient="records")
            response = requests.post(f"{API_BASE_URL}/tax/deductions", json={"expenses": expenses})

            if response.status_code == 200:
                suggestions = response.json().get("suggestions", [])
                if suggestions:
                    suggestions_df = pd.DataFrame(suggestions)
                    st.subheader("Flagged Tax-Deductible Expenses")
                    st.dataframe(suggestions_df)
                else:
                    st.info("No tax-deductible expenses detected.")
            else:
                st.error(response.json().get("error", "Failed to fetch deduction suggestions."))
        except Exception as e:
            st.error(f"An error occurred while fetching tax deductions: {e}")
    else:
        st.info("Upload or input expenses to see AI deduction suggestions.")
