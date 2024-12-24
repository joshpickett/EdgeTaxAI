import { storage } from '../utils/storage';

class CacheManager {
  constructor() {
    this.defaultTimeToLive = 3600; // 1 hour in seconds
    this.prefix = 'report_cache_';
  }

  async set(key, data, timeToLive = this.defaultTimeToLive) {
    const cacheItem = {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + (timeToLive * 1000)
    };
    
    await storage.setItem(this.getCacheKey(key), JSON.stringify(cacheItem));
  }

  async get(key) {
    try {
      const cached = await storage.getItem(this.getCacheKey(key));
      if (!cached) return null;

      const cacheItem = JSON.parse(cached);
      if (Date.now() > cacheItem.expiresAt) {
        await this.delete(key);
        return null;
      }

      return cacheItem.data;
    } catch (error) {
      console.error('Cache retrieval error:', error);
      return null;
    }
  }

  async delete(key) {
    await storage.removeItem(this.getCacheKey(key));
  }

  async clear() {
    const keys = await storage.getAllKeys();
    const cacheKeys = keys.filter(key => key.startsWith(this.prefix));
    await Promise.all(cacheKeys.map(key => storage.removeItem(key)));
  }

  getCacheKey(key) {
    return `${this.prefix}${key}`;
  }
}

export const cacheManager = new CacheManager();
