import streamlit as st
import requests
from config import API_BASE_URL

def reports_page():
    """
    Reports Page: Fetch and generate PDF/CSV reports for user expenses.
    """
    st.title("Generate Reports")
    st.markdown("#### Download IRS-ready PDF or CSV reports for your expenses.")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to access your reports.")
        return

    user_id = st.session_state["user_id"]

    # Fetch and Generate Reports
    if st.button("Generate Reports"):
        with st.spinner("Generating reports..."):
            try:
                response = requests.get(f"{API_BASE_URL}/reports/{user_id}")

                if response.status_code == 200:
                    reports_data = response.json().get("reports", [])
                    if reports_data:
                        st.success("Reports generated successfully! Download your reports below.")

                        # Provide Download Buttons
                        st.download_button(
                            label="Download PDF Report",
                            data=reports_data.get("pdf"),
                            file_name="expense_report.pdf",
                            mime="application/pdf"
                        )
                        st.download_button(
                            label="Download CSV Report",
                            data=reports_data.get("csv"),
                            file_name="expense_report.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No reports available. Please add expenses to generate a report.")
                else:
                    st.error(response.json().get("error", "Failed to generate reports."))
            except Exception as e:
                st.error("An unexpected error occurred while generating reports.")
                st.exception(e)
