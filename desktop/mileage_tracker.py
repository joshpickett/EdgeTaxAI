import streamlit as st
import requests

def mileage_tracker_page(api_base_url):
    """
    Mileage Tracker Page: Calculate mileage between two locations via API.
    """
    st.title("Mileage Tracker")
    st.markdown("#### Enter start and end locations to calculate mileage.")

    start_location = st.text_input("Start Location", placeholder="Enter starting address")
    end_location = st.text_input("End Location", placeholder="Enter destination address")

    if st.button("Calculate Mileage"):
        if not start_location or not end_location:
            st.error("Both start and end locations are required.")
        else:
            try:
                payload = {"start": start_location, "end": end_location}
                response = requests.post(f"{api_base_url}/mileage", json=payload)

                if response.status_code == 200:
                    distance = response.json().get("distance")
                    st.success(f"Total Distance: {distance}")
                else:
                    error = response.json().get("error", "Failed to calculate mileage.")
                    st.error(f"Error: {error}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
