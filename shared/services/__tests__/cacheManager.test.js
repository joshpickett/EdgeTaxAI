import { cacheManager } from '../cacheManager';
import { storage } from '../../utils/storage';

jest.mock('../../utils/storage');

describe('CacheManager', () => {
  beforeEach(() => {
    storage.setItem = jest.fn();
    storage.getItem = jest.fn();
    storage.removeItem = jest.fn();
    storage.getAllKeys = jest.fn();
  });

  test('should store data with expiration', async () => {
    const testData = { test: 'data' };
    await cacheManager.set('test-key', testData);

    expect(storage.setItem).toHaveBeenCalled();
    const storedData = JSON.parse(storage.setItem.mock.calls[0][1]);
    expect(storedData.data).toEqual(testData);
    expect(storedData.expiresAt).toBeDefined();
  });

  test('should return null for expired cache', async () => {
    const expiredCache = {
      data: { test: 'data' },
      timestamp: Date.now() - 7200000, // 2 hours ago
      expiresAt: Date.now() - 3600000  // 1 hour ago
    };
    storage.getItem.mockResolvedValueOnce(JSON.stringify(expiredCache));

    const result = await cacheManager.get('test-key');
    expect(result).toBeNull();
    expect(storage.removeItem).toHaveBeenCalled();
  });

  test('should clear all cached items', async () => {
    storage.getAllKeys.mockResolvedValueOnce([
      'report_cache_key1',
      'report_cache_key2',
      'other_key'
    ]);

    await cacheManager.clear();

    expect(storage.removeItem).toHaveBeenCalledTimes(2);
  });

  test('should handle storage errors gracefully', async () => {
    storage.getItem.mockRejectedValueOnce(new Error('Storage error'));

    const result = await cacheManager.get('test-key');
    expect(result).toBeNull();
  });
});
