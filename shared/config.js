// Shared configuration for both platforms
const config = {
  // API Configuration
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:5000',
    timeout: 30000,
    retryAttempts: 3,
    headers: {
      'Content-Type': 'application/json'
    }
  },

  // Authentication Configuration
  auth: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    tokenExpiry: 24 * 60 * 60 * 1000, // 24 hours
    refreshThreshold: 5 * 60 * 1000 // 5 minutes
  },

  // Platform-specific Settings
  platforms: {
    mobile: {
      storage: 'asyncStorage',
      biometricSupport: true
    },
    desktop: {
      storage: 'localStorage',
      biometricSupport: process.platform === 'darwin' || process.platform === 'win32'
    }
  },

  // Shared Feature Flags
  features: {
    enableBiometric: true,
    enableOfflineMode: true,
    enableAutoSync: true
  },

  // Error Messages
  errors: {
    network: 'Network error occurred',
    auth: 'Authentication failed',
    validation: 'Validation error'
  },

  // Validation Rules
  validation: {
    password: {
      minLength: 8,
      requireSpecialCharacter: true,
      requireNumber: true
    },
    email: {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    }
  }
};

export default config;
