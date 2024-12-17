import streamlit as st
import requests
import logging
from config import API_BASE_URL

# Configure Logging
logging.basicConfig(
    filename="bank_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def bank_integration_page():
    """
    Bank Integration Page: Allows users to connect bank accounts and fetch transactions via the API.
    """
    st.title("Bank Integration")
    st.markdown("#### Connect your bank accounts for automatic expense tracking.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to connect your bank accounts.")
        logging.error("Unauthorized access: User not logged in.")
        return

    user_id = st.session_state["user_id"]

    # Step 1: Connect Bank Account
    st.subheader("Connect Bank Account")
    bank_name = st.text_input("Bank Name", placeholder="E.g., Chase, Bank of America")

    if bank_name and not bank_name.isalnum():
        st.error("Bank name can only contain letters and numbers.")
        logging.warning(f"Invalid bank name input: {bank_name}")
        return

    if st.button("Connect Bank"):
        if not bank_name:
            st.error("Bank name is required.")
            logging.warning("User attempted to connect bank without providing a name.")
        else:
            try:
                payload = {"user_id": user_id, "bank_name": bank_name}
                response = requests.post(f"{API_BASE_URL}/banks/connect", json=payload)

                if response.status_code == 200:
                    st.success(f"Successfully connected to {bank_name}!")
                    logging.info(f"User {user_id} successfully connected to bank: {bank_name}")
                else:
                    error_message = response.json().get("error", "Failed to connect bank account.")
                    st.error(error_message)
                    logging.error(f"Error connecting to bank: {error_message}")
            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                logging.exception(f"Exception while connecting to bank: {e}")

    # Step 2: Fetch Bank Transactions
    st.subheader("Fetch Bank Transactions")
    if st.button("Fetch Transactions"):
        try:
            response = requests.get(f"{API_BASE_URL}/banks/transactions/{user_id}")

            if response.status_code == 200:
                transactions = response.json().get("transactions", [])
                if transactions:
                    st.subheader("Bank Transactions")
                    st.dataframe(transactions)
                    logging.info(f"User {user_id} fetched bank transactions successfully.")
                else:
                    st.info("No transactions found for the connected accounts.")
                    logging.info(f"User {user_id} has no transactions in connected accounts.")
            else:
                error_message = response.json().get("error", "Failed to fetch transactions.")
                st.error(error_message)
                logging.error(f"Error fetching transactions: {error_message}")
        except Exception as e:
            st.error("An unexpected error occurred while fetching transactions.")
            logging.exception(f"Exception while fetching transactions: {e}")
