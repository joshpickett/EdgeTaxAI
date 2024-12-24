import streamlit as st
import requests
import logging
from utils.validators import validate_email, validate_phone, validate_password

def account_creation_page(api_base_url):
    st.title("Create Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    def validate_inputs():
        errors = []
        if not validate_email(email):
            errors.append("Invalid email format")
        if not validate_phone(phone_number):
            errors.append("Invalid phone number format")
        if not validate_password(password):
            errors.append("Password must be at least 8 characters with numbers and special characters")
        return errors

    if st.button("Create Account"):
        if all([full_name, email, phone_number, password]):
            errors = validate_inputs()
            if not errors:
                payload = {
                    "full_name": full_name,
                    "email": email,
                    "phone_number": phone_number,
                    "password": password
                }
                response = requests.post(f"{api_base_url}/auth/signup", json=payload)
            else:
                for error in errors:
                    st.error(error)
                return
        else:
            st.error("All fields are required.")
