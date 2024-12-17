import streamlit as st

# API Base URL
API_BASE_URL = "http://localhost:5000/api"  # Update this URL for production deployment

# Import pages
from login_page import login_page
from account_creation import account_creation_page
from dashboard import dashboard_page
from add_expense import add_expense_page
from reports_page import reports_page
from password_reset import password_reset_page
from bank_integration import bank_integration_page
from mileage_tracker import mileage_tracker_page
from quarterly_tax_reminders import quarterly_tax_reminders_page

def main():
    """
    Streamlit App Navigation Logic.
    This serves as the entry point for the TaxEdgeAI Desktop App.
    """
    st.sidebar.title("TaxEdgeAI Navigation")
    
    # Sidebar navigation menu
    page = st.sidebar.radio(
        "Select Page",
        [
            "Login",
            "Create Account",
            "Password Reset",
            "Dashboard",
            "Add Expense",
            "Bank Integration",
            "Mileage Tracker",
            "Tax Reminders",
            "Reports"
        ]
    )

    # Page rendering logic
    if page == "Login":
        login_page(API_BASE_URL)
    elif page == "Create Account":
        account_creation_page(API_BASE_URL)
    elif page == "Password Reset":
        password_reset_page(API_BASE_URL)
    elif page == "Dashboard":
        dashboard_page(API_BASE_URL)
    elif page == "Add Expense":
        add_expense_page(API_BASE_URL)
    elif page == "Bank Integration":
        bank_integration_page(API_BASE_URL)
    elif page == "Mileage Tracker":
        mileage_tracker_page(API_BASE_URL)
    elif page == "Tax Reminders":
        quarterly_tax_reminders_page(API_BASE_URL)
    elif page == "Reports":
        reports_page(API_BASE_URL)
    else:
        st.error("Invalid Page Selection")

if __name__ == "__main__":
    main()
