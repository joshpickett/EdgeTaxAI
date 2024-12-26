import { AppError, errorCodes, handleError, throwIf } from '../errorHandler';

describe('ErrorHandler', () => {
  describe('AppError', () => {
    it('should create error with default values', () => {
      const error = new AppError('Test error');
      expect(error.message).toBe('Test error');
      expect(error.code).toBe('UNKNOWN_ERROR');
      expect(error.details).toEqual({});
      expect(error.timestamp).toBeDefined();
    });

    it('should create error with custom values', () => {
      const error = new AppError('Custom error', 'CUSTOM_CODE', { foo: 'bar' });
      expect(error.message).toBe('Custom error');
      expect(error.code).toBe('CUSTOM_CODE');
      expect(error.details).toEqual({ foo: 'bar' });
    });
  });

  describe('handleError', () => {
    it('should return AppError instance unchanged', () => {
      const originalError = new AppError('Test error');
      const handled = handleError(originalError);
      expect(handled).toBe(originalError);
    });

    it('should handle Application Programming Interface errors', () => {
      const applicationProgrammingInterfaceError = {
        response: {
          data: { message: 'Application Programming Interface Error message' },
          status: 400
        }
      };
      const handled = handleError(applicationProgrammingInterfaceError);
      expect(handled).toBeInstanceOf(AppError);
      expect(handled.code).toBe('APPLICATION_PROGRAMMING_INTERFACE_ERROR');
      expect(handled.details.status).toBe(400);
    });

    it('should handle network errors', () => {
      const networkError = {
        request: {},
        message: 'Network failure'
      };
      const handled = handleError(networkError);
      expect(handled).toBeInstanceOf(AppError);
      expect(handled.code).toBe('NETWORK_ERROR');
      expect(handled.details.originalError).toBe('Network failure');
    });

    it('should handle generic errors', () => {
      const error = new Error('Generic error');
      const handled = handleError(error);
      expect(handled).toBeInstanceOf(AppError);
      expect(handled.message).toBe('Generic error');
    });
  });

  describe('throwIf', () => {
    it('should throw AppError when condition is true', () => {
      expect(() => {
        throwIf(true, 'Test error');
      }).toThrow(AppError);
    });

    it('should not throw when condition is false', () => {
      expect(() => {
        throwIf(false, 'Test error');
      }).not.toThrow();
    });

    it('should throw with custom error code', () => {
      try {
        throwIf(true, 'Test error', 'CUSTOM_ERROR');
      } catch (error) {
        expect(error.code).toBe('CUSTOM_ERROR');
      }
    });
  });

  describe('errorCodes', () => {
    it('should contain all required error codes', () => {
      expect(errorCodes).toEqual({
        NETWORK_ERROR: 'NETWORK_ERROR',
        VALIDATION_ERROR: 'VALIDATION_ERROR',
        AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
        APPLICATION_PROGRAMMING_INTERFACE_ERROR: 'APPLICATION_PROGRAMMING_INTERFACE_ERROR',
        SYNC_ERROR: 'SYNC_ERROR'
      });
    });
  });
});
