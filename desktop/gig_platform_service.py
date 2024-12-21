import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "https://your-backend-api.com/api")

def get_oauth_link(platform):
    """
    Get the OAuth URL for a gig platform.
    """
    try:
        return f"{BASE_URL}/gig/connect/{platform}"
    except Exception as e:
        print(f"Error fetching OAuth link for {platform}: {e}")
        return None

def fetch_connected_platforms(user_id):
    """
    Fetch the list of connected platforms for a user.
    """
    try:
        response = requests.get(f"{BASE_URL}/gig/connections", params={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("connected_accounts", [])
        else:
            return []
    except Exception as e:
        print(f"Error fetching connected platforms: {e}")
        return []

def fetch_platform_data(user_id, platform):
    """
    Fetch data (trips, earnings) for a connected platform.
    """
    try:
        response = requests.get(f"{BASE_URL}/gig/fetch-data", params={"user_id": user_id, "platform": platform})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data from {platform}"}
    except Exception as e:
        print(f"Error fetching data from {platform}: {e}")
        return {"error": str(e)}
