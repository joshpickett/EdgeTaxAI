const BASE_URL = "https://your-backend-api.com/api";
const SYNC_INTERVAL = 1800000; // 30 minutes
import { secureTokenStorage } from '../utils/secureTokenStorage';

export const PLATFORM_CONFIG = {
  uber: {
    oauth_url: 'https://login.uber.com/oauth/v2/authorize',
    token_url: 'https://login.uber.com/oauth/v2/token',
    refresh_url: 'https://login.uber.com/oauth/v2/refresh',
    earnings_url: 'https://api.uber.com/v1.2/partners/payments',
    processor: 'uber',
    sync_enabled: true,
    auto_sync: true
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

// Function to sync platform data
export const syncPlatformData = async (platform, userId) => {
  try {
    const response = await fetch(`${BASE_URL}/gig/sync`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform, user_id: userId })
    });

    if (!response.ok) {
      throw new Error(`Failed to sync ${platform} data`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Sync Data Error for ${platform}:`, error.message);
    throw error;
  }
};

// Function to get sync status
export const getSyncStatus = async (platform, userId) => {
  try {
    const response = await fetch(
      `${BASE_URL}/gig/sync-status?platform=${platform}&user_id=${userId}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get sync status for ${platform}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Sync status error for ${platform}:`, error.message);
    throw error;
  }
};

// Token management functions
export const storePlatformToken = async (platform, userId, tokenData) => {
  const key = `token_${platform}_${userId}`;
  return await secureTokenStorage.storeToken(key, JSON.stringify(tokenData));
};

export const getPlatformToken = async (platform, userId) => {
  const key = `token_${platform}_${userId}`;
  const tokenData = await secureTokenStorage.getToken(key);
  if (!tokenData) return null;
  
  const parsed = JSON.parse(tokenData);
  if (isTokenExpired(parsed)) {
    return await refreshPlatformToken(platform, userId, parsed.refresh_token);
  }
  return parsed.access_token;
};

export const refreshPlatformToken = async (platform, userId, refreshToken) => {
  try {
    const response = await fetch(`${BASE_URL}/gig/refresh-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform, refresh_token: refreshToken })
    });
    
    if (!response.ok) throw new Error('Token refresh failed');
    
    const newTokenData = await response.json();
    await storePlatformToken(platform, userId, newTokenData);
    return newTokenData.access_token;
  } catch (error) {
    console.error(`Token refresh error for ${platform}:`, error);
    throw error;
  }
};
