import streamlit as st
import requests

def login_page(api_base_url):
    """
    Login Page: Allows users to log in using their email or phone and password.
    """
    st.title("Login")

    # Input Fields
    identifier = st.text_input("Email or Phone", placeholder="Enter your email or phone")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    # Login Button
    if st.button("Login"):
        if not identifier or not password:
            st.error("Both fields are required.")
            return
        
        try:
            # Prepare and send API request
            payload = {"identifier": identifier, "password": password}
            response = requests.post(f"{api_base_url}/auth/login", json=payload)

            if response.status_code == 200:
                # On success, store user_id in session state
                user_data = response.json()
                st.session_state["user_id"] = user_data["user_id"]
                st.success("Login successful! Redirecting...")
            else:
                # Display error message from API
                st.error(response.json().get("error", "Invalid email/phone or password."))
        except Exception as e:
            # Handle any network or unexpected errors
            st.error(f"An error occurred: {e}")
