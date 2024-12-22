import { Platform } from 'react-native';

class Logger {
  constructor() {
    this.logs = [];
    this.maxLogs = 1000;
  }

  info(message, data = {}) {
    this._log('INFO', message, data);
  }

  warn(message, data = {}) {
    this._log('WARN', message, data);
  }

  error(message, error = null, data = {}) {
    this._log('ERROR', message, { ...data, error: error?.message || error });
  }

  debug(message, data = {}) {
    if (__DEV__) {
      this._log('DEBUG', message, data);
    }
  }

  _log(level, message, data) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      platform: Platform.OS,
      version: Platform.Version
    };

    this.logs.unshift(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.pop();
    }

    if (__DEV__) {
      console.log(`[${level}] ${message}`, data);
    }
  }

  getLogs() {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }

  exportLogs() {
    return JSON.stringify(this.logs, null, 2);
  }
}

export const logger = new Logger();
