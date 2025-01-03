// shared/services/unifiedAuthService.ts

import { SharedValidator } from '../utils/validators';
import { SessionService } from './sessionService';
import { TokenService } from './tokenService';

export class UnifiedAuthService {
  private static instance: UnifiedAuthService;
  private tokenService: TokenService;
  private sessionService: SessionService;

  private constructor() {
    this.tokenService = TokenService.getInstance();
    this.sessionService = SessionService.getInstance();
  }

  static getInstance(): UnifiedAuthService {
    if (!UnifiedAuthService.instance) {
      UnifiedAuthService.instance = new UnifiedAuthService();
    }
    return UnifiedAuthService.instance;
  }

  async login(credentials: any): Promise<any> {
    const errors = SharedValidator.validateAuth(credentials);
    if (errors.length > 0) {
      throw new Error(errors[0].message);
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      this.tokenService.setTokens(data.accessToken, data.refreshToken);
      this.sessionService.createSession({
        userId: data.userId,
        deviceInfo: navigator.userAgent,
        lastActivity: new Date(),
      });

      return data;
    } catch (error) {
      throw error;
    }
  }

  async verifyOTP(data: any): Promise<any> {
    const errors = SharedValidator.validateAuth(data);
    if (errors.length > 0) {
      throw new Error(errors[0].message);
    }

    try {
      const response = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('OTP verification failed');
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  logout(): void {
    this.tokenService.clearTokens();
    // Clear session
  }
}