// Shared constants for both platforms
export const AUTH_STATES = {
  LOGGED_OUT: 'LOGGED_OUT',
  LOGGING_IN: 'LOGGING_IN',
  LOGGED_IN: 'LOGGED_IN',
  ERROR: 'ERROR'
};

export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  AUTH: 'AUTH_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  SERVER: 'SERVER_ERROR'
};

export const PLATFORMS = {
  UBER: 'uber',
  LYFT: 'lyft',
  DOORDASH: 'doordash',
  INSTACART: 'instacart'
};

export const EXPENSE_CATEGORIES = {
  MILEAGE: 'mileage',
  MAINTENANCE: 'maintenance',
  INSURANCE: 'insurance',
  PHONE: 'phone',
  SUPPLIES: 'supplies',
  OTHER: 'other'
};

export const TAX_CATEGORIES = {
  DEDUCTIBLE: 'deductible',
  NON_DEDUCTIBLE: 'non_deductible',
  PARTIAL: 'partial'
};

export const SYNC_STATES = {
  IDLE: 'idle',
  SYNCING: 'syncing',
  COMPLETED: 'completed',
  ERROR: 'error'
};

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh'
  },
  EXPENSES: {
    CREATE: '/expenses',
    LIST: '/expenses/list',
    UPDATE: '/expenses/update',
    DELETE: '/expenses/delete'
  },
  PLATFORMS: {
    CONNECT: '/platforms/connect',
    DISCONNECT: '/platforms/disconnect',
    SYNC: '/platforms/sync'
  }
};

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  SETTINGS: 'settings'
};

export const EVENT_TYPES = {
  AUTH_CHANGE: 'auth_change',
  SYNC_STATUS: 'sync_status',
  ERROR: 'error'
};
