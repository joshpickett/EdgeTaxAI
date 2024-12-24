import {
  PLATFORM_CONFIG,
  connectPlatform,
  fetchConnectedPlatforms,
  fetchPlatformData,
  connectApiKeyPlatform,
  syncPlatformData,
  getSyncStatus,
  storePlatformToken,
  getPlatformToken,
  refreshPlatformToken
} from '../gigPlatformService';
import { secureTokenStorage } from '../../utils/secureTokenStorage';

// Mock dependencies
jest.mock('../../utils/secureTokenStorage');

describe('GigPlatformService', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    global.fetch = jest.fn();
    global.console.error = jest.fn();
  });

  describe('Platform Configuration', () => {
    it('should have correct platform configurations', () => {
      expect(PLATFORM_CONFIG).toHaveProperty('uber');
      expect(PLATFORM_CONFIG).toHaveProperty('lyft');
      expect(PLATFORM_CONFIG).toHaveProperty('doordash');
      
      expect(PLATFORM_CONFIG.uber).toHaveProperty('oauth_url');
      expect(PLATFORM_CONFIG.uber).toHaveProperty('token_url');
      expect(PLATFORM_CONFIG.uber).toHaveProperty('refresh_url');
    });
  });

  describe('connectPlatform', () => {
    it('should return OAuth URL for valid platform', async () => {
      const platform = 'uber';
      const result = await connectPlatform(platform);
      expect(result).toBe(PLATFORM_CONFIG[platform].oauth_url);
    });

    it('should handle invalid platform', async () => {
      await expect(connectPlatform('invalid-platform'))
        .rejects.toThrow('Failed to connect to invalid-platform.');
    });
  });

  describe('fetchConnectedPlatforms', () => {
    const mockUserId = 'user123';

    it('should fetch connected platforms successfully', async () => {
      const mockPlatforms = ['uber', 'lyft'];
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ connected_accounts: mockPlatforms })
      });

      const result = await fetchConnectedPlatforms(mockUserId);
      expect(result).toEqual(mockPlatforms);
    });

    it('should handle fetch error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Fetch failed' })
      });

      await expect(fetchConnectedPlatforms(mockUserId))
        .rejects.toThrow('Failed to fetch connected platforms.');
    });
  });

  describe('fetchPlatformData', () => {
    const mockUserId = 'user123';
    const platform = 'uber';

    beforeEach(() => {
      getPlatformToken.mockResolvedValue('mock-token');
    });

    it('should fetch platform data successfully', async () => {
      const mockData = { trips: [] };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: mockData })
      });

      const result = await fetchPlatformData(platform, mockUserId);
      expect(result).toEqual(mockData);
    });

    it('should handle missing token', async () => {
      getPlatformToken.mockResolvedValueOnce(null);

      await expect(fetchPlatformData(platform, mockUserId))
        .rejects.toThrow('No valid token for uber');
    });

    it('should handle unsupported platform', async () => {
      await expect(fetchPlatformData('invalid', mockUserId))
        .rejects.toThrow('Unsupported platform: invalid');
    });
  });

  describe('Token Management', () => {
    const platform = 'uber';
    const mockUserId = 'user123';
    const mockTokenData = {
      access_token: 'access123',
      refresh_token: 'refresh123',
      expires_at: Date.now() + 3600000
    };

    describe('storePlatformToken', () => {
      it('should store token successfully', async () => {
        await storePlatformToken(platform, mockUserId, mockTokenData);
        expect(secureTokenStorage.storeToken).toHaveBeenCalledWith(
          `token_${platform}_${mockUserId}`,
          JSON.stringify(mockTokenData)
        );
      });
    });

    describe('getPlatformToken', () => {
      it('should return valid token', async () => {
        secureTokenStorage.getToken.mockResolvedValueOnce(
          JSON.stringify(mockTokenData)
        );

        const token = await getPlatformToken(platform, mockUserId);
        expect(token).toBe(mockTokenData.access_token);
      });

      it('should refresh expired token', async () => {
        const expiredToken = {
          ...mockTokenData,
          expires_at: Date.now() - 1000
        };
        secureTokenStorage.getToken.mockResolvedValueOnce(
          JSON.stringify(expiredToken)
        );

        await getPlatformToken(platform, mockUserId);
        expect(refreshPlatformToken).toHaveBeenCalled();
      });
    });

    describe('refreshPlatformToken', () => {
      it('should refresh token successfully', async () => {
        const newTokenData = {
          access_token: 'new-access',
          refresh_token: 'new-refresh'
        };
        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(newTokenData)
        });

        const result = await refreshPlatformToken(
          platform,
          mockUserId,
          'refresh123'
        );
        expect(result).toBe(newTokenData.access_token);
      });

      it('should handle refresh failure', async () => {
        global.fetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ error: 'Refresh failed' })
        });

        await expect(refreshPlatformToken(platform, mockUserId, 'refresh123'))
          .rejects.toThrow('Token refresh failed');
      });
    });
  });

  describe('Platform Sync', () => {
    const platform = 'uber';
    const mockUserId = 'user123';

    describe('syncPlatformData', () => {
      it('should sync data successfully', async () => {
        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true })
        });

        const result = await syncPlatformData(platform, mockUserId);
        expect(result).toEqual({ success: true });
      });

      it('should handle sync failure', async () => {
        global.fetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ error: 'Sync failed' })
        });

        await expect(syncPlatformData(platform, mockUserId))
          .rejects.toThrow('Failed to sync uber data');
      });
    });

    describe('getSyncStatus', () => {
      it('should get sync status successfully', async () => {
        const mockStatus = { lastSync: Date.now() };
        global.fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockStatus)
        });

        const result = await getSyncStatus(platform, mockUserId);
        expect(result).toEqual(mockStatus);
      });

      it('should handle status fetch failure', async () => {
        global.fetch.mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({ error: 'Status fetch failed' })
        });

        await expect(getSyncStatus(platform, mockUserId))
          .rejects.toThrow('Failed to get sync status for uber');
      });
    });
  });
});
