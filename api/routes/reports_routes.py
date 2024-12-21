import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from config import API_BASE_URL
from ..utils.db_utils import get_db_connection
from ..utils.ai_utils import generate_tax_insights

def reports_page():
    """
    Streamlit Reports Page:
    - Generate IRS-ready reports.
    - Generate custom reports.
    - Manage gig platform connections and fetch trip/expense data.
    """
    st.title("Reports Dashboard")
    st.markdown("#### View, Generate, and Manage Reports")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to view reports.")
        return

    user_id = st.session_state["user_id"]

    # Section 1: IRS-Ready Reports
    st.subheader("IRS-Ready Reports")
    st.write("Generate and download IRS-ready reports as PDF or CSV.")

    if st.button("Generate IRS Report"):
        with st.spinner("Generating IRS Report..."):
            try:
                response = requests.get(f"{API_BASE_URL}/reports/{user_id}")
                if response.status_code == 200:
                    report_data = response.json()
                    st.success("IRS Report generated successfully!")
                    st.download_button(
                        label="Download PDF Report",
                        data=report_data["pdf"],
                        file_name="irs_report.pdf",
                        mime="application/pdf",
                    )
                    st.download_button(
                        label="Download CSV Report",
                        data=report_data["csv"],
                        file_name="irs_report.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Failed to generate IRS Report.")
            except Exception as e:
                st.error("An error occurred while generating IRS Report.")
                st.exception(e)

    # Section 2: IRS Schedule C Report
    st.subheader("IRS Schedule C Report")
    st.write("Download a pre-filled IRS Schedule C form based on categorized expenses.")
    if st.button("Generate Schedule C Report"):
        with st.spinner("Generating IRS Schedule C..."):
            try:
                url = f"{API_BASE_URL}/reports/generate-schedule-c?user_id={user_id}"
                st.markdown(
                    f"[Click here to download IRS Schedule C Report]({url})",
                    unsafe_allow_html=True,
                )
                st.success("IRS Schedule C Report generated successfully!")
            except Exception as e:
                st.error("Failed to generate IRS Schedule C Report.")
                st.exception(e)

    # Section 3: Custom Reports
    st.subheader("Custom Reports")
    st.write("Generate custom reports using filters like date range and category.")

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    category = st.text_input("Category (Optional)")

    if st.button("Generate Custom Report"):
        filters = {
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
            "category": category,
        }
        with st.spinner("Generating Custom Report..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/reports/custom/{user_id}",
                    json=filters,
                )
                if response.status_code == 200:
                    st.success("Custom Report generated successfully!")
                    st.download_button(
                        label="Download Custom Report",
                        data=response.content,
                        file_name="custom_report.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Failed to generate custom report.")
            except Exception as e:
                st.error("An error occurred while generating custom report.")
                st.exception(e)

    # Section 4: Gig Platform Integration
    st.subheader("Connect Gig Platforms")
    st.write(
        "Connect your gig platform accounts (e.g., Uber, Lyft, DoorDash, Instacart, Upwork, Fiverr) "
        "to import trip and expense data."
    )

    platforms = [
        {"name": "Uber", "endpoint": "uber"},
        {"name": "Lyft", "endpoint": "lyft"},
        {"name": "DoorDash", "endpoint": "doordash"},
        {"name": "Instacart", "endpoint": "instacart"},
        {"name": "Upwork", "endpoint": "upwork"},
        {"name": "Fiverr", "endpoint": "fiverr"},
    ]

    for platform in platforms:
        st.markdown(
            f"[Connect {platform['name']}]({API_BASE_URL}/gig/connect/{platform['endpoint']})",
            unsafe_allow_html=True,
        )

    # Display Connected Platforms
    st.subheader("Connected Platforms")
    try:
        response = requests.get(f"{API_BASE_URL}/gig/connections", params={"user_id": user_id})
        if response.status_code == 200:
            connected_accounts = response.json().get("connected_accounts", [])
            if connected_accounts:
                for account in connected_accounts:
                    st.write(f"✔ Connected: {account['platform'].capitalize()}")
            else:
                st.write("No connected platforms yet.")
        else:
            st.error("Failed to load connected platforms.")
    except Exception as e:
        st.error("An error occurred while fetching connected platforms.")
        st.exception(e)

    # Section 5: Fetch Gig Platform Data
    st.subheader("Fetch Trip and Expense Data")
    platform_choice = st.selectbox(
        "Select a Platform", ["Uber", "Lyft", "DoorDash", "Instacart", "Upwork", "Fiverr"]
    )

    if st.button("Fetch Data"):
        with st.spinner(f"Fetching data from {platform_choice}..."):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/gig/fetch-data",
                    params={"user_id": user_id, "platform": platform_choice.lower()},
                )
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    if data:
                        st.success(f"Fetched data from {platform_choice} successfully!")
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.write(f"No data available for {platform_choice}.")
                else:
                    st.error(f"Failed to fetch data from {platform_choice}.")
            except Exception as e:
                st.error(f"An error occurred while fetching data from {platform_choice}.")
                st.exception(e)

    # New Section: Generate Tax Report
    st.subheader("Generate Tax Report")
    if st.button("Generate Tax Report"):
        with st.spinner("Generating Tax Report..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate-tax-report",
                    json={"user_id": user_id, "year": datetime.now().year}
                )
                if response.status_code == 200:
                    report_data = response.json()
                    st.success("Tax Report generated successfully!")
                    st.json(report_data)
                else:
                    st.error("Failed to generate tax report.")
            except Exception as e:
                st.error("An error occurred while generating tax report.")
                st.exception(e)

    # New Section: Generate Tax Insights
    st.subheader("Generate Tax Insights")
    if st.button("Generate Tax Insights"):
        with st.spinner("Generating Tax Insights..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/tax-report",
                    json={"user_id": user_id, "year": datetime.now().year}
                )
                if response.status_code == 200:
                    insights_data = response.json()
                    st.success("Tax Insights generated successfully!")
                    st.json(insights_data)
                else:
                    st.error("Failed to generate tax insights.")
            except Exception as e:
                st.error("An error occurred while generating tax insights.")
                st.exception(e)


if __name__ == "__main__":
    reports_page()
