import streamlit as st
import requests

def add_expense_page(api_base_url):
    st.title("Add Expense")

    if "user_id" not in st.session_state:
        st.error("Please log in to add expenses.")
        return

    description = st.text_input("Expense Description")
    amount = st.number_input("Amount ($)", min_value=0.01)
    category = st.text_input("Category")

    if st.button("Add Expense"):
        payload = {
            "user_id": st.session_state["user_id"],
            "description": description,
            "amount": amount,
            "category": category
        }
        response = requests.post(f"{api_base_url}/expenses/add", json=payload)
        if response.status_code == 200:
            st.success("Expense added successfully!")
        else:
            st.error(response.json().get("error", "Failed to add expense."))
