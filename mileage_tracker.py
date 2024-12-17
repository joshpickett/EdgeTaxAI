#Mileage Plan Tracker Page on App

import streamlit as st
import requests

def mileage_tracker_page(api_base_url):
    """
    Mileage Tracker Page: Calculate mileage between two locations via API.
    """
    st.title("Mileage Tracker")
    st.markdown("#### Track your work-related mileage.")

    if "user_id" not in st.session_state:
        st.error("Please log in to track mileage.")
        return

    start_location = st.text_input("Start Location")
    end_location = st.text_input("End Location")

    if st.button("Calculate Mileage"):
        if not start_location or not end_location:
            st.error("Both start and end locations are required.")
        else:
            try:
                payload = {"start": start_location, "end": end_location}
                response = requests.post(f"{api_base_url}/tax/mileage", json=payload)

                if response.status_code == 200:
                    distance = response.json().get("distance")
                    st.success(f"Total Distance: {distance} miles")
                else:
                    st.error(response.json().get("error", "Failed to calculate mileage."))
            except Exception as e:
                st.error(f"An error occurred: {e}")
