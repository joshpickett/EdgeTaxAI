from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import streamlit as st
import requests


def password_reset_page(api_base_url):
    """
    Password Reset Page: Allows users to reset their password via API.
    """
    st.title("Reset Password")

    email = st.text_input("Enter your registered Email")
    new_password = st.text_input("Enter New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password"):
        if not email or not new_password or not confirm_password:
            st.error("All fields are required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                payload = {"email": email, "new_password": new_password}
                response = requests.post(f"{api_base_url}/auth/reset", json=payload)

                if response.status_code == 200:
                    st.success(
                        "Password reset successfully! Please log in with your new password."
                    )
                else:
                    st.error(response.json().get("error", "Failed to reset password."))
            except Exception as e:
                st.error(f"An error occurred: {e}")
