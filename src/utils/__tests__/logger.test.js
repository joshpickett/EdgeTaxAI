import { logger } from '../logger';
import { Platform } from 'react-native';

describe('Logger', () => {
  beforeEach(() => {
    logger.clearLogs();
    console.log = jest.fn();
    // Mock Date.toISOString for consistent timestamps
    jest.spyOn(Date.prototype, 'toISOString').mockReturnValue('2023-01-01T00:00:00.000Z');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Logging', () => {
    it('should log info messages', () => {
      logger.info('Test info message', { data: 'test' });
      const logs = logger.getLogs();
      
      expect(logs[0]).toEqual({
        timestamp: '2023-01-01T00:00:00.000Z',
        level: 'INFO',
        message: 'Test info message',
        data: { data: 'test' },
        platform: Platform.OS,
        version: Platform.Version
      });
    });

    it('should log warning messages', () => {
      logger.warn('Test warning', { warning: true });
      const logs = logger.getLogs();
      
      expect(logs[0].level).toBe('WARN');
      expect(logs[0].data).toEqual({ warning: true });
    });

    it('should log error messages with error objects', () => {
      const error = new Error('Test error');
      logger.error('Error occurred', error, { context: 'test' });
      const logs = logger.getLogs();
      
      expect(logs[0].level).toBe('ERROR');
      expect(logs[0].data.error).toBe('Test error');
      expect(logs[0].data.context).toBe('test');
    });

    it('should log debug messages only in development', () => {
      const originalDevelopment = global.__DEV__;
      global.__DEV__ = true;
      
      logger.debug('Debug message', { debug: true });
      let logs = logger.getLogs();
      expect(logs[0].level).toBe('DEBUG');

      global.__DEV__ = false;
      logger.debug('Should not log', { debug: false });
      logs = logger.getLogs();
      expect(logs.length).toBe(1); // Previous log remains
      
      global.__DEV__ = originalDevelopment;
    });
  });

  describe('Log Management', () => {
    it('should maintain maximum log count', () => {
      const maximumLogs = logger.maxLogs;
      for (let i = 0; i < maximumLogs + 10; i++) {
        logger.info(`Log ${i}`);
      }
      
      const logs = logger.getLogs();
      expect(logs.length).toBe(maximumLogs);
      expect(logs[0].message).toBe(`Log ${maximumLogs + 9}`);
    });

    it('should clear logs successfully', () => {
      logger.info('Test log');
      expect(logger.getLogs()).toHaveLength(1);
      
      logger.clearLogs();
      expect(logger.getLogs()).toHaveLength(0);
    });

    it('should export logs in JSON format', () => {
      logger.info('Test log');
      const exported = logger.exportLogs();
      
      expect(typeof exported).toBe('string');
      expect(JSON.parse(exported)).toEqual(logger.getLogs());
    });
  });

  describe('Error Handling', () => {
    it('should handle undefined error objects', () => {
      logger.error('Error message', undefined, { context: 'test' });
      const logs = logger.getLogs();
      
      expect(logs[0].data.error).toBeUndefined();
    });

    it('should handle non-Error objects', () => {
      logger.error('Error message', 'string error', { context: 'test' });
      const logs = logger.getLogs();
      
      expect(logs[0].data.error).toBe('string error');
    });

    it('should handle circular references', () => {
      const circularData = { self: null };
      circularData.self = circularData;
      
      logger.info('Circular reference', circularData);
      const exported = logger.exportLogs();
      
      expect(() => JSON.parse(exported)).not.toThrow();
    });
  });

  describe('Development Mode', () => {
    it('should console.log in development mode', () => {
      const originalDevelopment = global.__DEV__;
      global.__DEV__ = true;
      
      logger.info('Test log');
      expect(console.log).toHaveBeenCalled();
      
      global.__DEV__ = originalDevelopment;
    });

    it('should not console.log in production mode', () => {
      const originalDevelopment = global.__DEV__;
      global.__DEV__ = false;
      
      logger.info('Test log');
      expect(console.log).not.toHaveBeenCalled();
      
      global.__DEV__ = originalDevelopment;
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty messages', () => {
      logger.info('');
      const logs = logger.getLogs();
      expect(logs[0].message).toBe('');
    });

    it('should handle null data', () => {
      logger.info('Test message', null);
      const logs = logger.getLogs();
      expect(logs[0].data).toBeNull();
    });

    it('should handle undefined data', () => {
      logger.info('Test message', undefined);
      const logs = logger.getLogs();
      expect(logs[0].data).toEqual({});
    });
  });
});
