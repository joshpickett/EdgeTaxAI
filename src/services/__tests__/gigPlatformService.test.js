import { 
  connectPlatform, 
  fetchConnectedPlatforms,
  fetchPlatformData,
  syncPlatformData,
  PLATFORM_CONFIG 
} from '../gigPlatformService';
import { secureTokenStorage } from '../../utils/secureTokenStorage';

jest.mock('../../utils/secureTokenStorage');

describe('Gig Platform Service', () => {
  beforeEach(() => {
    fetch.mockClear();
    secureTokenStorage.getToken.mockClear();
    secureTokenStorage.storeToken.mockClear();
  });

  describe('connectPlatform', () => {
    it('returns correct OAuth URL for platform', async () => {
      const platform = 'uber';
      const url = await connectPlatform(platform);
      expect(url).toBe(PLATFORM_CONFIG[platform].oauth_url);
    });

    it('throws error for invalid platform', async () => {
      await expect(connectPlatform('invalid')).rejects.toThrow();
    });
  });

  describe('fetchConnectedPlatforms', () => {
    it('fetches connected platforms successfully', async () => {
      const mockPlatforms = ['uber', 'lyft'];
      fetch.mockResponseOnce(JSON.stringify({ connected_accounts: mockPlatforms }));

      const result = await fetchConnectedPlatforms('user123');
      expect(result).toEqual(mockPlatforms);
    });

    it('handles API errors', async () => {
      fetch.mockResponseOnce(JSON.stringify({ error: 'API Error' }), { status: 400 });
      await expect(fetchConnectedPlatforms('user123')).rejects.toThrow();
    });
  });

  describe('fetchPlatformData', () => {
    it('fetches platform data with valid token', async () => {
      const mockData = { trips: [] };
      secureTokenStorage.getToken.mockResolvedValueOnce(JSON.stringify({ access_token: 'token' }));
      fetch.mockResponseOnce(JSON.stringify({ data: mockData }));

      const result = await fetchPlatformData('uber', 'user123');
      expect(result).toEqual(mockData);
    });

    it('handles missing token', async () => {
      secureTokenStorage.getToken.mockResolvedValueOnce(null);
      await expect(fetchPlatformData('uber', 'user123')).rejects.toThrow('No valid token');
    });
  });

  describe('syncPlatformData', () => {
    it('syncs platform data successfully', async () => {
      const mockResponse = { success: true };
      fetch.mockResponseOnce(JSON.stringify(mockResponse));

      const result = await syncPlatformData('uber', 'user123');
      expect(result).toEqual(mockResponse);
    });

    it('handles sync errors', async () => {
      fetch.mockResponseOnce(JSON.stringify({ error: 'Sync failed' }), { status: 500 });
      await expect(syncPlatformData('uber', 'user123')).rejects.toThrow();
    });
  });
});
