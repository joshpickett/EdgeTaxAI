import streamlit as st
import requests
from login_page import show_login_page  # Import the login page logic

# Check if user is authenticated (OTP Verified)
def check_auth():
    """
    Check if the user is authenticated. If not, redirect to the login page.
    """
    if "user_id" not in st.session_state or not st.session_state["user_id"]:
        st.warning("Please log in to continue.")
        show_login_page()  # Show the OTP-based login page
        st.stop()

# Logout Function
def logout():
    """
    Clears session state and logs the user out.
    """
    st.session_state.clear()  # Clear all session variables
    st.success("Logged out successfully!")
    st.experimental_rerun()  # Reload the app to show the login page

# Main Application Function
def main():
    """
    Main application entry point with navigation.
    """
    st.title("Welcome to EdgeTaxAI")

    # Check if the user is logged in
    check_auth()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Reports", "Tax Optimization", "Logout"]
    )

    # Logout Option
    if menu == "Logout":
        logout()
        return

    # Dashboard
    if menu == "Dashboard":
        st.subheader("Dashboard")
        st.write("This is the dashboard where you can manage your expenses and tax optimization.")

    # Reports
    elif menu == "Reports":
        st.subheader("Reports")
        st.write("This is where you can generate and view reports.")

    # Tax Optimization
    elif menu == "Tax Optimization":
        st.subheader("Tax Optimization")
        st.write("View your tax savings and deduction suggestions here.")

if __name__ == "__main__":
    # Initialize user session if not already set
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    main()
