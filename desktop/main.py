from src.screens.UnifiedDashboard import UnifiedDashboard
from src.components.auth.LoginForm import LoginForm

import streamlit as streamlit

def main():
    streamlit.title("EdgeTaxAI")
    
    if "user_id" not in streamlit.session_state:
        LoginForm(on_login=handle_login)
    else:
        UnifiedDashboard(
            user_id=streamlit.session_state.user_id,
            on_logout=handle_logout
        )

    # ...rest of the code...
