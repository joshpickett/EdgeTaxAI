const BASE_URL = "https://your-backend-api.com/api";

// Function to get the OAuth connection URL for a platform
export const connectPlatform = async (platform) => {
  try {
    const url = `${BASE_URL}/gig/connect/${platform}`;
    return url; // Return the OAuth URL for navigation
  } catch (error) {
    console.error(`Error connecting to ${platform}:`, error.message);
    throw new Error(`Failed to connect to ${platform}.`);
  }
};

// Function to fetch the list of connected platforms for a user
export const fetchConnectedPlatforms = async (userId) => {
  try {
    const response = await fetch(`${BASE_URL}/gig/connections?user_id=${userId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to fetch connected platforms.");
    }

    const data = await response.json();
    return data.connected_accounts || []; // Return list of connected accounts
  } catch (error) {
    console.error("Error fetching connected platforms:", error.message);
    throw error;
  }
};

// Function to fetch trip and earnings data from a connected platform
export const fetchPlatformData = async (platform, userId) => {
  try {
    const response = await fetch(
      `${BASE_URL}/gig/fetch-data?platform=${platform}&user_id=${userId}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch data from ${platform}.`);
    }

    const data = await response.json();
    return data.data; // Return fetched trip/expense data
  } catch (error) {
    console.error(`Fetch Data Error for ${platform}:`, error.message);
    throw error;
  }
};

// Function to connect DoorDash and Instacart with API keys
export const connectApiKeyPlatform = async (platform, apiKey) => {
  try {
    const response = await fetch(`${BASE_URL}/gig/api-key-connect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform, api_key: apiKey }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to connect ${platform}.`);
    }

    const data = await response.json();
    return data.message || `${platform} connected successfully.`;
  } catch (error) {
    console.error(`Error connecting ${platform} with API key:`, error.message);
    throw error;
  }
};
