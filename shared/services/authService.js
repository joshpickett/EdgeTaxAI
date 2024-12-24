import config from '../config';
import { handleApiError } from '../utils/errorHandler';
import { getStorageAdapter } from '../utils/storageAdapter';

class AuthService {
  constructor() {
    this.baseUrl = config.api.baseUrl;
    this.storage = getStorageAdapter();
  }

  async login(credentials) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      await this.setTokens(data.token, data.refreshToken);
      return data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async verifyOneTimePassword(identifier, oneTimePassword) {
    try {
      const response = await fetch(`${this.baseUrl}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, oneTimePassword })
      });

      if (!response.ok) {
        throw new Error('One-Time Password verification failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async refreshToken() {
    try {
      const refreshToken = await this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      await this.setTokens(data.token, data.refreshToken);
      return data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async setTokens(token, refreshToken) {
    await this.storage.setItem(config.auth.tokenKey, token);
    if (refreshToken) {
      await this.storage.setItem(config.auth.refreshTokenKey, refreshToken);
    }
  }

  async getToken() {
    return await this.storage.getItem(config.auth.tokenKey);
  }

  async getRefreshToken() {
    return await this.storage.getItem(config.auth.refreshTokenKey);
  }

  async clearTokens() {
    await this.storage.removeItem(config.auth.tokenKey);
    await this.storage.removeItem(config.auth.refreshTokenKey);
  }

  async isAuthenticated() {
    const token = await this.getToken();
    return !!token;
  }
}

export default new AuthService();
