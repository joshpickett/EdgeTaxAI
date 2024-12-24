import config from '../config';
import { AUTH_STATES, ERROR_TYPES } from '../constants';

class AuthService {
  constructor() {
    this.baseUrl = config.api.baseUrl;
    this.tokenKey = config.auth.tokenKey;
    this.refreshTokenKey = config.auth.refreshTokenKey;
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
      this.setTokens(data.token, data.refreshToken);
      return data;
    } catch (error) {
      throw new Error(error.message);
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
        throw new Error('One Time Password verification failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw new Error(error.message);
    }
  }

  async refreshToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      this.setTokens(data.token, data.refreshToken);
      return data;
    } catch (error) {
      throw new Error(error.message);
    }
  }

  setTokens(token, refreshToken) {
    localStorage.setItem(this.tokenKey, token);
    if (refreshToken) {
      localStorage.setItem(this.refreshTokenKey, refreshToken);
    }
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  clearTokens() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export default new AuthService();
