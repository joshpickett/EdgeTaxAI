import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
MILEAGE_ICON = ASSETS_DIR / 'logo' / 'icon' / 'edgetaxai-icon-color.svg'

def mileage_tracker_page(api_base_url):
    """
    Mileage Tracker Page: Calculate mileage between two locations via API.
    """
    st.title("Mileage Tracker")
    st.image(str(MILEAGE_ICON), width=50)
    st.markdown("#### Track your business mileage for tax deductions")

    # Add tabs for different mileage tracking options
    tab1, tab2 = st.tabs(["Track New Trip", "View History"])

    with tab1:
        track_new_trip(api_base_url)
    
    with tab2:
        view_trip_history(api_base_url)

def track_new_trip(api_base_url):
    start_location = st.text_input("Start Location", placeholder="Enter starting address")
    end_location = st.text_input("End Location", placeholder="Enter destination address")
    purpose = st.text_input("Business Purpose", placeholder="Enter trip purpose")
    date = st.date_input("Trip Date", value=datetime.now())

    recurring = st.checkbox("Make this a recurring trip?")
    if recurring:
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])

    if st.button("Calculate & Save Trip"):
        if not all([start_location, end_location, purpose]):
            st.error("All fields are required.")
        else:
            try:
                payload = {
                    "start": start_location,
                    "end": end_location,
                    "purpose": purpose,
                    "date": date.strftime("%Y-%m-%d"),
                    "recurring": recurring,
                    "frequency": frequency if recurring else None
                }

                response = requests.post(f"{api_base_url}/mileage", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Total Distance: {data['distance']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Distance", f"{data['distance']} miles")
                    with col2:
                        st.metric("Tax Deduction", f"${data['tax_deduction']:.2f}")
                    
                    if recurring:
                        st.success("Recurring trip pattern saved!")
                else:
                    error = response.json().get("error", "Failed to calculate mileage.")
                    st.error(f"Error: {error}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def view_trip_history(api_base_url):
    try:
        response = requests.get(f"{api_base_url}/mileage/history")
        if response.status_code == 200:
            trips = response.json()
            
            # Summary metrics
            total_miles = sum(trip['distance'] for trip in trips)
            total_deductions = sum(trip['tax_deduction'] for trip in trips)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Miles", f"{total_miles:.1f}")
            with col2:
                st.metric("Total Deductions", f"${total_deductions:.2f}")
            
            # Trip history table
            if trips:
                st.write("### Trip History")
                trip_data = []
                for trip in trips:
                    trip_data.append({
                        "Date": trip['date'],
                        "Route": f"{trip['start']} → {trip['end']}",
                        "Distance": f"{trip['distance']} mi",
                        "Purpose": trip['purpose'],
                        "Deduction": f"${trip['tax_deduction']:.2f}"
                    })
                st.table(trip_data)
            else:
                st.info("No trips recorded yet.")
    except Exception as e:
        st.error(f"Error fetching trip history: {e}")
