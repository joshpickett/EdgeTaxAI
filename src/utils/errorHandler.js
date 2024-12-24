export class AppError extends Error {
  constructor(message, code = 'UNKNOWN_ERROR', details = {}) {
    super(message);
    this.code = code;
    this.details = details;
    this.timestamp = new Date().toISOString();
  }
}

export const errorCodes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  API_ERROR: 'API_ERROR',
  SYNC_ERROR: 'SYNC_ERROR'
};

export const handleError = (error, context = '') => {
  console.error(`Error in ${context}:`, error);
  
  if (error instanceof AppError) {
    return error;
  }

  if (error.response) {
    return new AppError(
      error.response.data.message || 'API Error',
      'API_ERROR',
      { status: error.response.status }
    );
  }

  if (error.request) {
    return new AppError(
      'Network Error',
      'NETWORK_ERROR',
      { originalError: error.message }
    );
  }

  return new AppError(error.message);
};

export const throwIf = (condition, message, code = 'VALIDATION_ERROR') => {
  if (condition) {
    throw new AppError(message, code);
  }
};
