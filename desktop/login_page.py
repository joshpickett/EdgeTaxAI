import streamlit as st
import requests

def login_page(api_base_url):
    """
    Login Page: Allows users to log in using their email and password.
    Replaces direct database calls with an API request.
    """
    st.title("Login")

    # Input Fields
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Login Button
    if st.button("Login"):
        if email and password:
            try:
                # Prepare and send API request
                payload = {"email": email, "password": password}
                response = requests.post(f"{api_base_url}/auth/login", json=payload)

                if response.status_code == 200:
                    # On success, store user_id in session state
                    user_data = response.json()
                    st.session_state["user_id"] = user_data["user_id"]
                    st.success("Login successful! Redirecting...")
                else:
                    # Display error message from API
                    st.error(response.json().get("error", "Invalid email or password."))
            except Exception as e:
                # Handle any network or unexpected errors
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter both email and password.")
