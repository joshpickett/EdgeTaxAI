import streamlit as st
import requests
import re
from datetime import datetime
from config import API_BASE_URL

class ProfilePage:
    """
    Enhanced Profile Page with input validation, security features,
    and improved gig platform management
    """
    def __init__(self):
        self.user_id = st.session_state.get("user_id")

    def profile_page(self):
        """
        Streamlit Profile Page:
        - View and edit user profile.
        - Manage Gig Platform connections.
        """
        st.title("User Profile")

        # Check User Authentication
        if self.user_id is None:
            st.error("Please log in to view your profile.")
            return

        profile_data = None

        # Fetch Profile Data
        try:
            response = requests.get(f"{API_BASE_URL}/auth/profile", params={"user_id": self.user_id})
            if response.status_code == 200:
                profile_data = response.json()
            else:
                st.error("Failed to load profile data.")
                return
        except Exception as e:
            st.error("An error occurred while fetching profile data.")
            st.exception(e)
            return

        self.render_profile_section()

    def render_profile_section(self):
        """Render profile information section with validation"""
        st.subheader("Profile Information")
        
        # Profile tabs
        tabs = st.tabs([
            "Basic Info",
            "Tax Settings",
            "Gig Platforms",
            "Tax Documents",
            "Security",
            "Data Management"
        ])
        
        with tabs[0]:
            self.render_basic_info()
        
        with tabs[1]:
            self.render_tax_settings()
            
        with tabs[2]:
            self.render_gig_platforms()
            
        with tabs[3]:
            self.render_tax_documents()
            
        with tabs[4]:
            self.render_security_settings()
            
        with tabs[5]:
            self.render_data_management()

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None

    def render_basic_info(self):
        """Render basic information input fields"""
        full_name = st.text_input("Full Name", value="")
        email = st.text_input("Email", value="")
        phone_number = st.text_input("Phone Number", value="")

        # Update Profile
        if st.button("Update Profile"):
            if not self.validate_email(email):
                st.error("Invalid email format.")
            elif not self.validate_phone(phone_number):
                st.error("Invalid phone number format.")
            else:
                try:
                    payload = {
                        "full_name": full_name,
                        "email": email,
                        "phone_number": phone_number,
                    }
                    update_response = requests.put(f"{API_BASE_URL}/auth/profile", json=payload)
                    if update_response.status_code == 200:
                        st.success("Profile updated successfully!")
                    else:
                        st.error("Failed to update profile.")
                except Exception as e:
                    st.error("An error occurred while updating profile.")
                    st.exception(e)

    def render_tax_documents(self):
        """Render tax documents section"""
        st.subheader("Tax Documents")
        
        # Document categories
        doc_tabs = st.tabs(["Generated Documents", "Upload Documents", "Archive"])
        
        with doc_tabs[0]:
            self.show_generated_documents()
        
        with doc_tabs[1]:
            self.upload_tax_documents()
            
        with doc_tabs[2]:
            self.show_archived_documents()
    
    def show_generated_documents(self):
        """Display auto-generated tax documents"""
        st.subheader("Generated Tax Documents")
        
        # Year selector
        selected_year = st.selectbox(
            "Select Year",
            range(datetime.now().year, 2020, -1)
        )
        
        # Document types
        documents = {
            "Quarterly Summaries": [f"Q{i} {selected_year}" for i in range(1, 5)],
            "Annual Reports": [f"Annual Summary {selected_year}"],
            "Tax Forms": ["1099-NEC", "Schedule C Worksheet"]
        }
        
        for doc_type, doc_list in documents.items():
            st.write(f"### {doc_type}")
            for doc in doc_list:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(doc)
                with col2:
                    if st.button(f"Download {doc}"):
                        self.download_document(doc_type, doc, selected_year)

    def upload_tax_documents(self):
        """Upload tax documents section"""
        st.subheader("Upload Tax Documents")
        
        # Document type selector
        doc_type = st.selectbox(
            "Document Type",
            ["W-9", "1099-NEC", "Receipts", "Other"]
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "jpg", "png"],
            key="tax_doc_upload"
        )
        
        if uploaded_file:
            if st.button("Upload Document"):
                self.process_document_upload(uploaded_file, doc_type)

    def show_archived_documents(self):
        """Display archived tax documents"""
        st.subheader("Document Archive")
        
        # Year filter
        year_filter = st.multiselect(
            "Filter by Year",
            range(datetime.now().year, 2020, -1)
        )
        
        # Document type filter
        doc_type_filter = st.multiselect(
            "Filter by Type",
            ["W-9", "1099-NEC", "Receipts", "Quarterly Reports", "Annual Reports"]
        )
        
        if st.button("Apply Filters"):
            filtered_docs = self.get_filtered_documents(year_filter, doc_type_filter)
            for doc in filtered_docs:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(doc['name'])
                with col2:
                    st.write(doc['date'])
                with col3:
                    if st.button(f"Download {doc['name']}"):
                        self.download_archived_document(doc)

    def render_security_settings(self):
        """Render security settings section"""
        st.subheader("Security Settings")
        
        # Two-factor authentication
        enable_two_factor_authentication = st.toggle(
            "Enable Two-Factor Authentication",
            value=False
        )
        
        if enable_two_factor_authentication:
            st.info("Two-factor authentication is enabled")
            if st.button("Disable Two-Factor Authentication"):
                self.update_two_factor_authentication(False)
        else:
            if st.button("Enable Two-Factor Authentication"):
                self.update_two_factor_authentication(True)
        
        # Password change section
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Password"):
            if new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                self.update_password(current_password, new_password)

    def render_gig_platforms(self):
        """Render gig platform management section"""
        st.subheader("Gig Platform Management")
        
        try:
            # Fetch connected platforms
            connected_platforms = fetch_connected_platforms(self.user_id)
            
            if connected_platforms:
                st.write("Connected Platforms:")
                for platform in connected_platforms:
                    with st.expander(f"{platform['platform'].title()} Settings"):
                        # Platform status
                        status = validate_platform_connection(self.user_id, platform['platform'])
                        if status.connected:
                            st.success("Connected")
                            if status.last_sync:
                                st.write(f"Last synced: {status.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
                        else:
                            st.error("Connection error")
                            if status.error:
                                st.write(f"Error: {status.error}")
                        
                        # Sync settings
                        auto_sync = st.checkbox("Enable auto-sync", key=f"auto_sync_{platform['platform']}")
                        sync_frequency = st.select_slider(
                            "Sync frequency",
                            options=["Daily", "Weekly", "Monthly"],
                            key=f"sync_freq_{platform['platform']}"
                        )
            else:
                st.info("No platforms connected yet.")
                
        except Exception as e:
            st.error(f"Error loading gig platforms: {str(e)}")

if __name__ == "__main__":
    profile_page_instance = ProfilePage()
    profile_page_instance.profile_page()
