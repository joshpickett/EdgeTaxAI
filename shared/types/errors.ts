export enum ErrorType {
  NETWORK = 'NETWORK',
  VALIDATION = 'VALIDATION',
  AUTH = 'AUTH',
  TIMEOUT = 'TIMEOUT',
  SERVER = 'SERVER',
  UNKNOWN = 'UNKNOWN'
}

export interface ErrorContext {
  component?: string;
  operation?: string;
  retryCount: number;
  maxRetries: number;
  retryCallback?: () => Promise<void>;
  additionalData?: Record<string, any>;
}

export interface ErrorDetails {
  type: ErrorType;
  message: string;
  timestamp: string;
  context: ErrorContext;
  stack?: string;
}
