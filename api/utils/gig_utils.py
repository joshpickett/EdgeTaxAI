import os
import requests
import sqlite3
import logging
from typing import Dict, Any, List, Optional

# OAuth URLs for each platform
PLATFORM_OAUTH_URLS = {
    "uber": "https://login.uber.com/oauth/v2/authorize",
    "lyft": "https://www.lyft.com/oauth/authorize",
    "upwork": "https://www.upwork.com/ab/account-security/oauth2/authorize",
}

# Token Exchange URLs for each platform
PLATFORM_TOKEN_URLS = {
    "uber": "https://login.uber.com/oauth/v2/token",
    "lyft": "https://api.lyft.com/oauth/token",
    "upwork": "https://www.upwork.com/api/v3/oauth2/token",
}

# API Endpoints for Fetching Data
PLATFORM_API_URLS = {
    "uber": "https://api.uber.com/v1.2/history",
    "lyft": "https://api.lyft.com/v1/drivers/trips",
    "doordash": "https://api.doordash.com/v1/orders",
    "instacart": "https://api.instacart.com/v1/orders",
    "upwork": "https://www.upwork.com/api/v3/financial_reports",
    "fiverr": "https://api.fiverr.com/v1/seller/orders",
}

# Configure Logging
logging.basicConfig(
    filename="gig_platform.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function: Get OAuth URL for platform
def get_oauth_url(platform: str) -> Optional[str]:
    """
    Generates OAuth URL for the specified platform.
    """
    client_id = os.getenv(f"{platform.upper()}_CLIENT_ID")
    redirect_uri = os.getenv(f"{platform.upper()}_REDIRECT_URI")
    scope = "history profile" if platform in ["uber", "lyft"] else "default"

    if platform not in PLATFORM_OAUTH_URLS:
        return None

    return (
        f"{PLATFORM_OAUTH_URLS[platform]}?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
    )

# Function: Exchange Code for Access Token
def exchange_code_for_token(platform: str, code: str) -> Dict[str, Any]:
    """
    Exchanges the authorization code for an access token.
    """
    token_url = PLATFORM_TOKEN_URLS.get(platform)
    client_id = os.getenv(f"{platform.upper()}_CLIENT_ID")
    client_secret = os.getenv(f"{platform.upper()}_CLIENT_SECRET")
    redirect_uri = os.getenv(f"{platform.upper()}_REDIRECT_URI")

    if not token_url:
        raise ValueError(f"Token URL not configured for platform: {platform}")

    response = requests.post(token_url, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    })

    return response.json()

# Function: Store Tokens in Database
def store_platform_data(user_id: int, platform: str, token_data: Dict[str, Any]) -> None:
    """
    Stores access tokens in the database for the connected platform.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO connected_platforms (user_id, platform, access_token, refresh_token) "
        "VALUES (?, ?, ?, ?)",
        (user_id, platform, token_data.get("access_token"), token_data.get("refresh_token")),
    )

    conn.commit()
    conn.close()

# Function: Get Connected Platforms
def get_connected_accounts(user_id: int) -> List[Dict[str, str]]:
    """
    Fetches the list of platforms connected for a given user.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT platform FROM connected_platforms WHERE user_id = ?",
        (user_id,),
    )
    accounts = cursor.fetchall()
    conn.close()

    return [{"platform": account[0]} for account in accounts]

# Function: Fetch Access Token
def fetch_access_token(user_id: int, platform: str) -> Optional[str]:
    """
    Retrieves the access token for the specified platform and user.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT access_token FROM connected_platforms WHERE user_id = ? AND platform = ?",
        (user_id, platform),
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

# Function: Fetch Trip or Earnings Data
def fetch_trip_data(platform: str, access_token: str) -> Dict[str, Any]:
    """
    Fetch trip history or earnings data for the specified platform using the access token.
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    if platform not in PLATFORM_API_URLS:
        raise ValueError(f"No API endpoint configured for platform: {platform}")

    api_url = PLATFORM_API_URLS[platform]
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch data from {platform}. Status: {response.status_code}, Response: {response.text}"
        )
