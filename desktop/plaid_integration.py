import streamlit as st
import requests
import pandas as pd
import logging
from config import API_BASE_URL

# Configure Logging
logging.basicConfig(
    filename="plaid_integration.log",  # Logs stored in a file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def plaid_integration_page():
    """
    Plaid Integration Page: Connect user bank accounts and fetch transactions via API.
    """
    st.title("Bank Integration")
    st.markdown("#### Connect your bank accounts for automatic expense tracking.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to connect your bank accounts.")
        logging.error("Unauthorized access attempt: User not logged in.")
        return

    user_id = st.session_state["user_id"]

    # Step 1: Connect Bank Account
    st.subheader("Connect Bank Account")
    bank_name = st.text_input("Bank Name", placeholder="E.g., Chase, Bank of America")

    if bank_name and not bank_name.isalnum():
        st.error("Bank name can only contain letters and numbers.")
        logging.warning(f"Invalid bank name input by user {user_id}: {bank_name}")
        return

    if st.button("Connect Bank"):
        if not bank_name:
            st.error("Bank name is required.")
            logging.warning(f"User {user_id} attempted to connect bank without entering a bank name.")
        else:
            try:
                payload = {"user_id": user_id, "bank_name": bank_name}
                response = requests.post(f"{API_BASE_URL}/banks/connect", json=payload)

                if response.status_code == 200:
                    st.success(f"Successfully connected to {bank_name}!")
                    logging.info(f"User {user_id} successfully connected to bank: {bank_name}")
                else:
                    error_message = response.json().get("error", "Unknown error occurred.")
                    st.error(f"Failed to connect to {bank_name}: {error_message}")
                    logging.error(f"API Error - Connect Bank for user {user_id}: {error_message}")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.exception(f"Exception while connecting bank for user {user_id}: {e}")

    # Step 2: Fetch Bank Transactions
    st.subheader("Fetch Bank Transactions")
    if st.button("Fetch Transactions"):
        try:
            response = requests.get(f"{API_BASE_URL}/banks/transactions/{user_id}")

            if response.status_code == 200:
                transactions = response.json().get("transactions", [])
                if transactions:
                    st.subheader("Bank Transactions")
                    df = pd.DataFrame(transactions)
                    st.dataframe(df)
                    logging.info(f"User {user_id} fetched bank transactions successfully.")
                else:
                    st.info("No transactions found for the connected accounts.")
                    logging.info(f"User {user_id} has no transactions in connected accounts.")
            else:
                error_message = response.json().get("error", "Failed to fetch transactions.")
                st.error(error_message)
                logging.error(f"API Error - Fetch Transactions for user {user_id}: {error_message}")
        except Exception as e:
            st.error("An unexpected error occurred while fetching transactions.")
            logging.exception(f"Exception while fetching transactions for user {user_id}: {e}")
