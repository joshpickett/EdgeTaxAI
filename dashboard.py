import streamlit as st
import requests
import pandas as pd
from config import API_BASE_URL

def dashboard_page():
    """
    Dashboard Page: Fetch and display expenses dynamically with a loading spinner.
    """
    st.title("Dashboard")
    st.markdown("#### Overview of Your Expenses")

    # Validate User Session
    if "user_id" not in st.session_state:
        st.error("Please log in to view your dashboard.")
        return

    user_id = st.session_state["user_id"]

    # Fetch expenses with a loading spinner
    st.subheader("Your Expenses Summary")
    with st.spinner("Fetching your expenses..."):
        try:
            response = requests.get(f"{API_BASE_URL}/expenses/list/{user_id}")
            if response.status_code == 200:
                expenses = response.json().get("expenses", [])
                if expenses:
                    # Convert expenses into a DataFrame and display
                    df = pd.DataFrame(expenses)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No expenses found. Start adding your expenses!")
            else:
                st.error(response.json().get("error", "Failed to fetch expenses."))
        except Exception as e:
            st.error("An error occurred while fetching expenses.")
            st.exception(e)

    # Expense Summary Section
    st.subheader("Expense Overview")
    with st.spinner("Calculating expense summary..."):
        try:
            response = requests.get(f"{API_BASE_URL}/expenses/summary/{user_id}")
            if response.status_code == 200:
                summary = response.json()
                st.write(f"**Total Expenses:** ${summary.get('total_expenses', 0):,.2f}")
                st.write(f"**Number of Entries:** {summary.get('num_entries', 0)}")
            else:
                st.error(response.json().get("error", "Failed to fetch expense summary."))
        except Exception as e:
            st.error("An error occurred while calculating expense summary.")
            st.exception(e)

    # Visual Summary Section
    st.subheader("Expenses Breakdown")
    with st.spinner("Generating visual charts..."):
        try:
            response = requests.get(f"{API_BASE_URL}/expenses/breakdown/{user_id}")
            if response.status_code == 200:
                breakdown = response.json().get("breakdown", {})
                if breakdown:
                    df_breakdown = pd.DataFrame(list(breakdown.items()), columns=["Category", "Amount"])
                    st.bar_chart(df_breakdown.set_index("Category"))
                else:
                    st.info("No data available for expense breakdown.")
            else:
                st.error(response.json().get("error", "Failed to fetch expense breakdown."))
        except Exception as e:
            st.error("An error occurred while generating visual charts.")
            st.exception(e)
