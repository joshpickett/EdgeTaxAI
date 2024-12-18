import streamlit as st
import requests

def account_creation_page(api_base_url):
    st.title("Create Account")

    # Input Fields
    full_name = st.text_input("Full Name")
    email_or_phone = st.text_input("Email or Phone")  # Unified email/phone field
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        # Input Validation
        if not all([full_name, email_or_phone, password, confirm_password]):
            st.error("All fields are required.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Prepare Payload
        payload = {
            "full_name": full_name,
            "email_or_phone": email_or_phone,
            "password": password
        }

        # API Request
        try:
            response = requests.post(f"{api_base_url}/auth/signup", json=payload)
            if response.status_code == 201:
                st.success("Account created successfully! Please log in.")
            else:
                st.error(response.json().get("error", "Failed to create account."))
        except Exception as e:
            st.error(f"An error occurred: {e}")
