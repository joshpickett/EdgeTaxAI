import streamlit as st
import requests
import pandas as pd
import logging
from config import API_BASE_URL

# Configure Logging
logging.basicConfig(
    filename="plaid_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
PLAID_CATEGORIES = {
    "FOOD_AND_DRINK": "Meals",
    "TRAVEL": "Travel",
    "TRANSPORTATION": "Vehicle"
}

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
    
    if st.button("Connect Bank Account"):
        try:
            response = requests.post(f"{API_BASE_URL}/api/banks/plaid/link-token", 
                                   json={"user_id": user_id})

            if response.status_code == 200:
                link_token = response.json().get("link_token")
                # Initialize Plaid Link here

        except Exception as e:
            st.error("An unexpected error occurred while connecting to the bank.")
            logging.exception(f"Exception while connecting to bank: {e}")

    # Step 2: Fetch Bank Transactions
    st.subheader("Fetch Bank Transactions")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")

    if st.button("Fetch Transactions"):
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "user_id": user_id
            }
            response = requests.get(f"{API_BASE_URL}/api/banks/plaid/transactions", 
                                  params=params)

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

    # Add Balance Check Section
    st.subheader("Account Balances")
    if st.button("Check Balances"):
        try:
            response = requests.get(f"{API_BASE_URL}/api/banks/plaid/balance",
                                  params={"user_id": user_id})
            
            if response.status_code == 200:
                balances = response.json().get("balances", [])
                if balances:
                    for balance in balances:
                        st.write(f"Account: {balance['account_id']}")
                        st.write(f"Balance: ${balance['balance']:,.2f}")
                        st.write(f"Type: {balance['type']}")
                        st.write("---")
            else:
                st.error("Failed to fetch account balances")
        except Exception as e:
            st.error("Error checking balances")
            logging.error(f"Balance check error: {e}")

    # Add Disconnect Bank Option
    st.subheader("Manage Bank Connections")
    if st.button("Disconnect Bank"):
        if st.confirm("Are you sure you want to disconnect your bank account?"):
            try:
                response = requests.post(f"{API_BASE_URL}/api/banks/plaid/disconnect",
                                       json={"user_id": user_id})
                
                if response.status_code == 200:
                    st.success("Bank account disconnected successfully")
                else:
                    st.error("Failed to disconnect bank account")
            except Exception as e:
                st.error("Error disconnecting bank account")
                logging.error(f"Disconnect error: {e}")
