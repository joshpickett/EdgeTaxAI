import streamlit as st
import requests

def account_creation_page(api_base_url):
    st.title("Create Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if all([full_name, email, phone_number, password]):
            payload = {
                "full_name": full_name,
                "email": email,
                "phone_number": phone_number,
                "password": password
            }
            response = requests.post(f"{api_base_url}/auth/signup", json=payload)
            if response.status_code == 201:
                st.success("Account created successfully! Please login.")
            else:
                st.error(response.json().get("error", "Failed to create account."))
        else:
            st.error("All fields are required.")
