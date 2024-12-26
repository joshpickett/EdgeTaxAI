import tokenStorage from '../tokenStorage';

describe('TokenStorage', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  // Mock localStorage
  const localStorageMock = {
    getItem: jest.spyOn(window.localStorage, 'getItem'),
    setItem: jest.spyOn(window.localStorage, 'setItem'),
    removeItem: jest.spyOn(window.localStorage, 'removeItem'),
    clear: jest.spyOn(window.localStorage, 'clear'),
  };

  describe('setTokens', () => {
    it('should store tokens in localStorage', () => {
      tokenStorage.setTokens('test-token', 'refresh-token');
      expect(localStorage.getItem('auth_token')).toBe('test-token');
      expect(localStorage.getItem('refresh_token')).toBe('refresh-token');
    });

    it('should store only auth token if refresh token is not provided', () => {
      tokenStorage.setTokens('test-token');
      expect(localStorage.getItem('auth_token')).toBe('test-token');
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });

  describe('getToken', () => {
    it('should retrieve auth token from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      expect(tokenStorage.getToken()).toBe('test-token');
    });

    it('should return null if token does not exist', () => {
      expect(tokenStorage.getToken()).toBeNull();
    });
  });

  describe('getRefreshToken', () => {
    it('should retrieve refresh token from localStorage', () => {
      localStorage.setItem('refresh_token', 'refresh-token');
      expect(tokenStorage.getRefreshToken()).toBe('refresh-token');
    });
  });

  describe('clearTokens', () => {
    it('should remove both tokens from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('refresh_token', 'refresh-token');
      
      tokenStorage.clearTokens();
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when auth token exists', () => {
      localStorage.setItem('auth_token', 'test-token');
      expect(tokenStorage.isAuthenticated()).toBe(true);
    });

    it('should return false when auth token does not exist', () => {
      expect(tokenStorage.isAuthenticated()).toBe(false);
    });
  });
});
