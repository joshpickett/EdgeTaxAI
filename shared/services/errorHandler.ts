import { ErrorType, ErrorDetails, ErrorContext } from '../types/errors';

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorCallbacks: ((error: Error, context: ErrorContext) => void)[] = [];

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  handleError(error: Error, context: ErrorContext): void {
    const enhancedError = this.enhanceError(error, context);
    this.logError(enhancedError, context);
    this.notifyCallbacks(enhancedError, context);

    if (this.shouldRetry(enhancedError, context)) {
      return this.handleRetry(enhancedError, context);
    }

    throw enhancedError;
  }

  private enhanceError(error: Error, context: ErrorContext): Error {
    const enhancedError = error as any;
    enhancedError.timestamp = new Date().toISOString();
    enhancedError.context = context;
    enhancedError.type = this.determineErrorType(error);
    
    return enhancedError;
  }

  private determineErrorType(error: Error): ErrorType {
    if (error.name === 'NetworkError') return ErrorType.NETWORK;
    if (error.name === 'ValidationError') return ErrorType.VALIDATION;
    if (error.name === 'AuthError') return ErrorType.AUTH;
    return ErrorType.UNKNOWN;
  }

  private shouldRetry(error: Error, context: ErrorContext): boolean {
    return (
      context.retryCount < context.maxRetries &&
      this.isRetryableError(error)
    );
  }

  private isRetryableError(error: Error): boolean {
    const retryableTypes = [
      ErrorType.NETWORK,
      ErrorType.TIMEOUT,
      ErrorType.SERVER
    ];
    return retryableTypes.includes((error as any).type);
  }

  private async handleRetry(error: Error, context: ErrorContext): Promise<void> {
    const delay = Math.pow(2, context.retryCount) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    if (context.retryCallback) {
      await context.retryCallback();
    }
  }

  private logError(error: Error, context: ErrorContext): void {
    console.error('Error occurred:', {
      error,
      context,
      timestamp: new Date().toISOString()
    });
  }

  addErrorCallback(callback: (error: Error, context: ErrorContext) => void): void {
    this.errorCallbacks.push(callback);
  }

  private notifyCallbacks(error: Error, context: ErrorContext): void {
    this.errorCallbacks.forEach(callback => callback(error, context));
  }
}

export const errorHandler = ErrorHandler.getInstance();
