import streamlit as st
import requests
from config import API_BASE_URL

def profile_page():
    """
    Streamlit Profile Page:
    - View and edit user profile.
    - Manage Gig Platform connections.
    """
    st.title("User Profile")

    # Check User Authentication
    if "user_id" not in st.session_state:
        st.error("Please log in to view your profile.")
        return

    user_id = st.session_state["user_id"]
    profile_data = None

    # Fetch Profile Data
    try:
        response = requests.get(f"{API_BASE_URL}/auth/profile", params={"user_id": user_id})
        if response.status_code == 200:
            profile_data = response.json()
        else:
            st.error("Failed to load profile data.")
            return
    except Exception as e:
        st.error("An error occurred while fetching profile data.")
        st.exception(e)
        return

    # Display Profile Information
    st.subheader("Profile Information")
    full_name = st.text_input("Full Name", value=profile_data.get("full_name", ""))
    email = st.text_input("Email", value=profile_data.get("email", ""))
    phone_number = st.text_input("Phone Number", value=profile_data.get("phone_number", ""))

    # Update Profile
    if st.button("Update Profile"):
        try:
            payload = {
                "full_name": full_name,
                "email": email,
                "phone_number": phone_number,
            }
            update_response = requests.put(f"{API_BASE_URL}/auth/profile", json=payload)
            if update_response.status_code == 200:
                st.success("Profile updated successfully!")
            else:
                st.error("Failed to update profile.")
        except Exception as e:
            st.error("An error occurred while updating profile.")
            st.exception(e)

    # Gig Platform Integration
    st.subheader("Connect Gig Platforms")
    st.write("Manage your gig platform accounts to import trip and expense data.")

    platforms = [
        {"name": "Uber", "endpoint": "uber"},
        {"name": "Lyft", "endpoint": "lyft"},
        {"name": "DoorDash", "endpoint": "doordash"},
        {"name": "Instacart", "endpoint": "instacart"},
        {"name": "Upwork", "endpoint": "upwork"},
        {"name": "Fiverr", "endpoint": "fiverr"},
    ]

    for platform in platforms:
        if st.button(f"Connect {platform['name']}"):
            st.markdown(
                f"[Click here to connect {platform['name']}]({API_BASE_URL}/gig/connect/{platform['endpoint']})",
                unsafe_allow_html=True,
            )

    # Connected Accounts Section
    st.subheader("Connected Accounts")
    try:
        connection_response = requests.get(f"{API_BASE_URL}/gig/connections", params={"user_id": user_id})
        if connection_response.status_code == 200:
            connected_accounts = connection_response.json().get("connected_accounts", [])
            if connected_accounts:
                for account in connected_accounts:
                    st.write(f"✅ Connected: {account['platform'].capitalize()}")
            else:
                st.write("No connected accounts yet.")
        else:
            st.error("Failed to load connected accounts.")
    except Exception as e:
        st.error("An error occurred while fetching connected accounts.")
        st.exception(e)

if __name__ == "__main__":
    profile_page()
