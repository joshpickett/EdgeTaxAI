from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional
from ..utils.db_utils import get_db_connection
from ..utils.error_handler import handle_api_error
from ..utils.report_generator import ReportGenerator
import pandas as pd
import io
import os

reports_bp = Blueprint('reports', __name__)
report_generator = ReportGenerator()

@reports_bp.route("/generate-report", methods=["POST"])
def generate_report():
    """Generate comprehensive expense report"""
    try:
        data = request.json
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type', 'summary')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        report = report_generator.generate_expense_summary(
            user_id, start_date, end_date
        )
        
        return jsonify(report)
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return handle_api_error(e)

@reports_bp.route("/quarterly-summary", methods=["POST"])
def generate_quarterly_summary():
    """Generate quarterly expense and tax summary"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        quarter = data.get('quarter')

        if not user_id or not quarter:
            return jsonify({"error": "User ID and quarter are required"}), 400

        # Logic to generate quarterly summary
        # ...

    except Exception as e:
        logging.error(f"Error generating quarterly summary: {e}")
        return handle_api_error(e)

@reports_bp.route("/tax-summary", methods=["POST"])
def generate_tax_summary():
    """Generate tax summary report"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        summary = report_generator.generate_tax_summary(user_id, year)
        return jsonify(summary)
        
    except Exception as e:
        logging.error(f"Error generating tax summary: {e}")
        return handle_api_error(e)

@reports_bp.route("/irs/schedule-c", methods=["POST"])
def generate_schedule_c():
    """Generate IRS Schedule C report"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        schedule_c = report_generator.generate_schedule_c(user_id, year)
        return jsonify(schedule_c)
    except Exception as e:
        logging.error(f"Error generating Schedule C: {e}")
        return handle_api_error(e)

@reports_bp.route("/custom-report", methods=["POST"])
def generate_custom_report():
    """Generate custom report based on user specifications"""
    try:
        data = request.json
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        categories = data.get('categories', [])
        report_type = data.get('report_type', 'detailed')
        format_type = data.get('format', 'json')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        report = report_generator.generate_custom_report(
            user_id, 
            start_date, 
            end_date,
            categories,
            report_type
        )
        
        if format_type == 'csv':
            csv_data = report_generator.export_to_csv(report)
            return send_file(
                io.StringIO(csv_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'custom_report_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        
        return jsonify(report)
    except Exception as e:
        logging.error(f"Error generating custom report: {e}")
        return handle_api_error(e)

@reports_bp.route("/analytics", methods=["POST"])
def generate_analytics():
    """Generate expense pattern analytics"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        analytics = report_generator.generate_analytics(user_id, year)
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error generating analytics: {e}")
        return handle_api_error(e)

@reports_bp.route("/tax-savings", methods=["POST"])
def analyze_tax_savings():
    """Analyze potential tax saving opportunities"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        savings = report_generator.analyze_tax_savings(user_id, year)
        return jsonify(savings)
    except Exception as e:
        logging.error(f"Error analyzing tax savings: {e}")
        return handle_api_error(e)

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
