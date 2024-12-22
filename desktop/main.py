import streamlit as streamlit
import requests
import os
from urllib.parse import urlencode
from bank_integration import bank_integration_page
from gig_platform_service import get_oauth_link, fetch_connected_platforms, fetch_platform_data, handle_oauth_callback
from login_page import show_login_page  # Import the login page logic
from datetime import datetime
from pathlib import Path

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
APP_ICON = ASSETS_DIR / 'logo' / 'app-icon' / 'app-icon-android.png'
FAVICON = ASSETS_DIR / 'logo' / 'favicon' / 'favicon.ico'

# Check if user is logged in
def check_auth():
    if "user_id" not in streamlit.session_state or not streamlit.session_state["user_id"]:
        streamlit.warning("Please log in to continue.")
        show_login_page()
        streamlit.stop()

# Main Application Function
def main():
    streamlit.title("Welcome to EdgeTaxAI")
    streamlit.set_page_config(page_title="EdgeTaxAI", page_icon=str(FAVICON))
    
    # Authentication Check
    check_auth()

    # Sidebar Navigation
    streamlit.sidebar.title("Navigation")
    menu = streamlit.sidebar.radio(
        "Go to",
        ["Dashboard", "Bank Integration", "Gig Platforms", 
         "Reports", "Tax Optimization", "Logout"]
    )

    # Logout Button in Sidebar
    if menu == "Logout":
        streamlit.session_state.clear()  # Clear session state
        streamlit.success("Logged out successfully!")
        streamlit.experimental_rerun()  # Rerun the app to go back to login
        return

    # Dashboard
    if menu == "Dashboard":
        streamlit.subheader("Dashboard")
        streamlit.write("This is the dashboard where you can manage your expenses and tax optimization.")

    # Bank Integration
    elif menu == "Bank Integration":
        bank_integration_page()
        
    # Gig Platforms
    elif menu == "Gig Platforms":
        streamlit.subheader("Gig Platform Integration")
        
        # Generate redirect URI
        redirect_uri = f"{os.getenv('APP_URL')}/oauth-callback"
        
        streamlit.info("Connect your gig economy platforms to automatically import earnings and expenses.")
        # Handle OAuth callback
        params = streamlit.experimental_get_query_params()
        if 'code' in params and 'platform' in params:
            try:
                code = params['code'][0]
                platform = params['platform'][0]
                user_id = streamlit.session_state["user_id"]
                
                with streamlit.spinner(f"Connecting to {platform}..."):
                    success = handle_oauth_callback(
                        code=code,
                        platform=platform,
                        user_id=user_id
                    )
                    if success:
                        streamlit.success(f"Successfully connected to {platform}!")
                        streamlit.experimental_set_query_params()  # Clear URL parameters
                    else:
                        streamlit.error(f"Failed to connect to {platform}")

        # Show connected platforms
        connected_platforms = fetch_connected_platforms(streamlit.session_state["user_id"])
        
        if connected_platforms:
            streamlit.write("Connected Platforms:")
            for platform in connected_platforms:
                col1, col2, col3 = streamlit.columns([2,1,1])
                with col1:
                    streamlit.write(platform["platform"].title())
                with col2:
                    sync_button = streamlit.button(f"Sync {platform['platform']}", key=f"sync_{platform['platform']}")
                    if sync_button:
                        with streamlit.spinner(f"Syncing {platform['platform']} data..."):
                            try:
                                data = fetch_platform_data(streamlit.session_state["user_id"], platform["platform"])
                                if "error" not in data:
                                    streamlit.success(f"Successfully synced {platform['platform']} data!")
                                    # Show sync summary
                                    streamlit.write("Sync Summary:")
                                    streamlit.write(f"- Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    streamlit.write(f"- Earnings: ${data.get('earnings', 0):.2f}")
                                    streamlit.write(f"- Trips: {len(data.get('trips', []))}")
                                else:
                                    streamlit.error(f"Failed to sync {platform['platform']}: {data['error']}")
                            except Exception as e:
                                streamlit.error(f"Sync failed: {str(e)}")
                with col3:
                    status = get_sync_status(streamlit.session_state["user_id"], platform["platform"])
                    streamlit.write(f"Last sync: {status.get('last_sync', 'Never')}")

        # Platform connection buttons
        streamlit.write("Connect New Platform:")
        platforms = ["uber", "lyft", "doordash", "instacart"]
        for platform in platforms:
            if streamlit.button(f"Connect {platform.title()}", key=f"connect_{platform}"):
                oauth_url = get_oauth_link(
                    platform=platform,
                    redirect_uri=redirect_uri
                )
                if oauth_url:
                    params = urlencode({"platform": platform})
                    full_url = f"{oauth_url}&{params}"
                    streamlit.markdown(f"[Connect to {platform.title()}]({full_url})")
                else:
                    streamlit.error(f"Failed to get connection link for {platform}")

    # Reports
    elif menu == "Reports":
        streamlit.subheader("Reports")
        streamlit.write("This is where you can generate and view reports.")

    # Tax Optimization
    elif menu == "Tax Optimization":
        streamlit.subheader("Tax Optimization")
        streamlit.write("View your tax savings and deduction suggestions here.")

if __name__ == "__main__":
    if "user_id" not in streamlit.session_state:
        streamlit.session_state["user_id"] = None  # Initialize user session
    main()
