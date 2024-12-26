import AuthService from '../authService';
import config from '../../config';
import { storage } from '../../utils/storage';

jest.mock('../../utils/storage');

describe('AuthService', () => {
  let authService;

  beforeEach(() => {
    authService = new AuthService();
    global.fetch = jest.fn();
    storage.setItem = jest.fn();
    storage.getItem = jest.fn();
    storage.removeItem = jest.fn();
  });

  test('login should store tokens on success', async () => {
    const mockResponse = {
      ok: true,
      json: () => Promise.resolve({
        token: 'test-token',
        refreshToken: 'test-refresh-token'
      })
    };
    global.fetch.mockResolvedValueOnce(mockResponse);

    await authService.login({ email: 'test@test.com', password: 'password' });
    
    expect(storage.setItem).toHaveBeenCalledWith(
      config.auth.tokenKey,
      'test-token'
    );
  });

  test('verifyOneTimePassword should handle invalid One-Time Password', async () => {
    const mockResponse = {
      ok: false,
      json: () => Promise.resolve({ error: 'Invalid One-Time Password' })
    };
    global.fetch.mockResolvedValueOnce(mockResponse);

    await expect(
      authService.verifyOneTimePassword('user@test.com', '123456')
    ).rejects.toThrow('One-Time Password verification failed');
  });

  test('refreshToken should update stored tokens', async () => {
    storage.getItem.mockResolvedValueOnce('old-refresh-token');
    
    const mockResponse = {
      ok: true,
      json: () => Promise.resolve({
        token: 'new-token',
        refreshToken: 'new-refresh-token'
      })
    };
    global.fetch.mockResolvedValueOnce(mockResponse);

    await authService.refreshToken();
    
    expect(storage.setItem).toHaveBeenCalledWith(
      config.auth.tokenKey,
      'new-token'
    );
  });

  test('isAuthenticated should return true when token exists', async () => {
    storage.getItem.mockResolvedValueOnce('valid-token');
    
    const result = await authService.isAuthenticated();
    expect(result).toBe(true);
  });
});
