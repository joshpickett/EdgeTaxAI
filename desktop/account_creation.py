import streamlit as st
import requests

def account_creation_page(api_base_url):
    """
    OTP-based Account Creation Page.
    Allows users to sign up using email or phone number and verify via OTP.
    """
    st.title("Create Account with OTP")

    # Input Fields
    email_or_phone = st.text_input("Email or Phone")  # Unified field for email/phone
    otp_code = st.text_input("OTP Code", max_chars=6, placeholder="Enter OTP")
    is_otp_sent = st.session_state.get("is_otp_sent", False)

    # State Management for OTP
    if "otp_sent" not in st.session_state:
        st.session_state["otp_sent"] = False

    # Step 1: Send OTP
    if not st.session_state["otp_sent"]:
        if st.button("Send OTP"):
            if not email_or_phone:
                st.error("Please enter your email or phone number.")
                return

            # Call API to send OTP
            try:
                response = requests.post(f"{api_base_url}/signup-otp", json={"identifier": email_or_phone})
                if response.status_code == 200:
                    st.success("OTP sent successfully! Please check your email or phone.")
                    st.session_state["otp_sent"] = True
                    st.session_state["identifier"] = email_or_phone
                else:
                    st.error(response.json().get("error", "Failed to send OTP."))
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Step 2: Verify OTP
    if st.session_state["otp_sent"]:
        if st.button("Verify OTP"):
            if not otp_code:
                st.error("Please enter the OTP.")
                return

            # Call API to verify OTP
            try:
                payload = {"identifier": st.session_state["identifier"], "otp_code": otp_code}
                response = requests.post(f"{api_base_url}/verify-signup-otp", json=payload)
                if response.status_code == 201:
                    st.success("Account created successfully! Please log in.")
                    st.session_state["otp_sent"] = False  # Reset OTP state
                else:
                    st.error(response.json().get("error", "Invalid or expired OTP."))
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Reset State
    if st.session_state["otp_sent"] and st.button("Cancel"):
        st.session_state["otp_sent"] = False
        st.experimental_rerun()


# Main Function Call
if __name__ == "__main__":
    api_base_url = "http://localhost:5000/api"  # Replace with your backend URL
    account_creation_page(api_base_url)
