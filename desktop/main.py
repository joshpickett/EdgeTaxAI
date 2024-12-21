import streamlit as st
import requests
from bank_integration import bank_integration_page
from login_page import show_login_page  # Import the login page logic

# Check if user is logged in
def check_auth():
    if "user_id" not in st.session_state or not st.session_state["user_id"]:
        st.warning("Please log in to continue.")
        show_login_page()
        st.stop()

# Main Application Function
def main():
    st.title("Welcome to EdgeTaxAI")
    
    # Authentication Check
    check_auth()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Bank Integration", "Reports", "Tax Optimization", "Logout"]
    )

    # Logout Button in Sidebar
    if menu == "Logout":
        st.session_state.clear()  # Clear session state
        st.success("Logged out successfully!")
        st.experimental_rerun()  # Rerun the app to go back to login
        return

    # Dashboard
    if menu == "Dashboard":
        st.subheader("Dashboard")
        st.write("This is the dashboard where you can manage your expenses and tax optimization.")

    # Bank Integration
    elif menu == "Bank Integration":
        bank_integration_page()
        
    # Reports
    elif menu == "Reports":
        st.subheader("Reports")
        st.write("This is where you can generate and view reports.")

    # Tax Optimization
    elif menu == "Tax Optimization":
        st.subheader("Tax Optimization")
        st.write("View your tax savings and deduction suggestions here.")

if __name__ == "__main__":
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None  # Initialize user session
    main()
