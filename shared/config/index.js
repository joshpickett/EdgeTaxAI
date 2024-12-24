// Shared configuration for both platforms
const config = {
  // API Configuration
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:5000',
    version: 'v1',
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
    refreshThreshold: 5 * 60 * 1000, // 5 minutes
    otpLength: 6,
    otpExpiry: 5 // minutes
  },

  // AI Service Configuration
  ai: {
    categorization: {
      confidenceThreshold: 0.7,
      enableOffline: true,
      batchSize: 100
    }
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
      requireSpecialChar: true,
      requireNumber: true
    },
    email: {
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    }
  },

  // Tax Configuration
  tax: {
    mileageRate: 0.655, // 2023 IRS rate
    standardDeduction: 12950, // 2023 standard deduction
    selfEmploymentTaxRate: 0.153 // 15.3% self-employment tax
  }
};

export default config;
