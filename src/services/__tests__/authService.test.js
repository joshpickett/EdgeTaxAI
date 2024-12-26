import { authService } from '../authService';
import { apiClient } from '../apiClient';
import { tokenStorage } from '../../utils/tokenStorage';

jest.mock('../apiClient');
jest.mock('../../utils/tokenStorage');

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('handles successful login', async () => {
      const mockResponse = { token: 'test-token', user: { id: 1 } };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await authService.login('test@example.com', 'password');

      expect(result).toEqual(mockResponse);
      expect(tokenStorage.setTokens).toHaveBeenCalledWith('test-token');
    });

    it('handles login failure', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Invalid credentials'));

      await expect(
        authService.login('test@example.com', 'wrong-password')
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('clears tokens and calls API', async () => {
      apiClient.post.mockResolvedValueOnce({ success: true });

      await authService.logout();

      expect(tokenStorage.clearTokens).toHaveBeenCalled();
      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');
    });
  });

  describe('verify One Time Password', () => {
    it('handles successful One Time Password verification', async () => {
      const mockResponse = { token: 'test-token' };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await authService.verifyOTP('123456');

      expect(result).toEqual(mockResponse);
      expect(tokenStorage.setTokens).toHaveBeenCalledWith('test-token');
    });

    it('handles One Time Password verification failure', async () => {
      apiClient.post.mockRejectedValueOnce(new Error('Invalid One Time Password'));

      await expect(authService.verifyOTP('000000')).rejects.toThrow('Invalid One Time Password');
    });
  });

  describe('refresh Token', () => {
    it('refreshes token successfully', async () => {
      const mockResponse = { token: 'new-token' };
      apiClient.post.mockResolvedValueOnce(mockResponse);

      const result = await authService.refreshToken('old-token');

      expect(result).toEqual(mockResponse);
      expect(tokenStorage.setTokens).toHaveBeenCalledWith('new-token');
    });
  });
});
