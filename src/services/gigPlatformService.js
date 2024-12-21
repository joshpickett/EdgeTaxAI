const BASE_URL = "https://your-backend-api.com/api";

const PLATFORM_CONFIG = {
  uber: {
    oauth_url: 'https://login.uber.com/oauth/v2/authorize',
    token_url: 'https://login.uber.com/oauth/v2/token',
    data_url: 'https://api.uber.com/v1.2/partners/trips',
    scopes: ['partner.trips', 'partner.payments']
  },
  lyft: {
    oauth_url: 'https://api.lyft.com/oauth/authorize',
    token_url: 'https://api.lyft.com/oauth/token',
    data_url: 'https://api.lyft.com/v1/rides',
    scopes: ['rides.read', 'offline']
  },
  doordash: {
    oauth_url: 'https://identity.doordash.com/connect/authorize',
    token_url: 'https://identity.doordash.com/connect/token',
    data_url: 'https://api.doordash.com/v1/deliveries',
    scopes: ['delivery_status', 'earnings']
  }
};

// Function to get the OAuth connection URL for a platform
export const connectPlatform = async (platform) => {
  try {
    const url = `${PLATFORM_CONFIG[platform].oauth_url}`;
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

// Function to fetch platform data
export const fetchPlatformData = async (platform, userId) => {
  try {
    if (!PLATFORM_CONFIG[platform]) {
      throw new Error(`Unsupported platform: ${platform}`);
    }

    const token = await getPlatformToken(platform, userId);
    if (!token) {
      throw new Error(`No valid token for ${platform}`);
    }

    const config = PLATFORM_CONFIG[platform];
    const response = await fetch(
      config.data_url,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
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
