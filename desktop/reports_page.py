import streamlit as st
import requests
import pandas as pd
from config import API_BASE_URL

def reports_page():
    """
    IRS-Ready Reports and Custom Report Generation for the Desktop App.
    """
    st.title("Reports Dashboard")
    st.markdown("#### Generate and Download IRS-Ready Reports or Custom Reports.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to view and generate reports.")
        return

    user_id = st.session_state["user_id"]

    # Section 1: Fetch and Download IRS-Ready Reports
    st.subheader("IRS-Ready Reports")
    if st.button("Fetch IRS-Ready Reports"):
        with st.spinner("Fetching IRS-ready reports..."):
            try:
                response = requests.get(f"{API_BASE_URL}/reports/{user_id}")
                if response.status_code == 200:
                    report_data = response.json()
                    st.success("IRS-Ready Reports Generated Successfully!")
                    st.download_button(
                        label="Download PDF Report",
                        data=report_data["pdf"],
                        file_name="irs_report.pdf",
                        mime="application/pdf"
                    )
                    st.download_button(
                        label="Download CSV Report",
                        data=report_data["csv"],
                        file_name="irs_report.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(response.json().get("error", "Failed to fetch IRS-ready reports."))
            except Exception as e:
                st.error("An error occurred while fetching IRS-ready reports.")
                st.exception(e)

    # Section 2: Custom Report Generation
    st.subheader("Generate Custom Reports")
    st.markdown("Use filters to generate custom reports for your expenses.")

    # Input Filters
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    category = st.text_input("Category (optional)")

    # Fetch Custom Report
    if st.button("Generate Custom Report"):
        filters = {}
        if start_date:
            filters["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            filters["end_date"] = end_date.strftime("%Y-%m-%d")
        if category:
            filters["category"] = category

        with st.spinner("Generating custom report..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/reports/custom/{user_id}",
                    json=filters
                )
                if response.status_code == 200:
                    st.success("Custom Report Generated Successfully!")
                    st.download_button(
                        label="Download Custom Report",
                        data=response.content,
                        file_name="custom_report.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(response.json().get("error", "Failed to generate custom report."))
            except Exception as e:
                st.error("An error occurred while generating the custom report.")
                st.exception(e)

if __name__ == "__main__":
    reports_page()
