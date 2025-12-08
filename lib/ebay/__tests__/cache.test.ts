/**
 * Cache Module Tests
 */

import { EbayCache } from '../cache';

// Mock ioredis
jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => {
    const store = new Map<string, { value: string; expiry: number }>();
    
    return {
      status: 'ready',
      get: jest.fn(async (key: string) => {
        const item = store.get(key);
        if (!item) return null;
        if (Date.now() > item.expiry) {
          store.delete(key);
          return null;
        }
        return item.value;
      }),
      setex: jest.fn(async (key: string, ttl: number, value: string) => {
        store.set(key, { value, expiry: Date.now() + ttl * 1000 });
        return 'OK';
      }),
      keys: jest.fn(async (pattern: string) => {
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return Array.from(store.keys()).filter(key => regex.test(key));
      }),
      del: jest.fn(async (...keys: string[]) => {
        let deleted = 0;
        keys.forEach(key => {
          if (store.delete(key)) deleted++;
        });
        return deleted;
      }),
      info: jest.fn(async () => 'used_memory_human:1.5M'),
      quit: jest.fn(async () => 'OK'),
      on: jest.fn()
    };
  });
});

describe('Cache Module', () => {
  let cache: EbayCache;

  beforeEach(() => {
    cache = new EbayCache('redis://localhost:6379');
  });

  afterEach(async () => {
    await cache.close();
  });

  describe('get and set', () => {
    it('should cache and retrieve data', async () => {
      const endpoint = 'findCompletedItems';
      const params = { keywords: 'pokemon' };
      const data = { items: [], totalResults: 0 };

      await cache.set(endpoint, params, data);
      const cached = await cache.get(endpoint, params);

      expect(cached).toEqual(data);
    });

    it('should return null for cache miss', async () => {
      const endpoint = 'findCompletedItems';
      const params = { keywords: 'pokemon' };

      const cached = await cache.get(endpoint, params);

      expect(cached).toBeNull();
    });

    it('should generate consistent keys for same params', async () => {
      const endpoint = 'findCompletedItems';
      const params1 = { keywords: 'pokemon', minPrice: 10 };
      const params2 = { minPrice: 10, keywords: 'pokemon' }; // Different order
      const data = { items: [], totalResults: 0 };

      await cache.set(endpoint, params1, data);
      const cached = await cache.get(endpoint, params2);

      expect(cached).toEqual(data);
    });

    it('should generate different keys for different params', async () => {
      const endpoint = 'findCompletedItems';
      const params1 = { keywords: 'pokemon' };
      const params2 = { keywords: 'yugioh' };
      const data1 = { items: [], totalResults: 0 };
      const data2 = { items: [], totalResults: 5 };

      await cache.set(endpoint, params1, data1);
      await cache.set(endpoint, params2, data2);

      const cached1 = await cache.get(endpoint, params1);
      const cached2 = await cache.get(endpoint, params2);

      expect(cached1).toEqual(data1);
      expect(cached2).toEqual(data2);
    });
  });

  describe('clear', () => {
    it('should clear all cache entries', async () => {
      await cache.set('findCompletedItems', { keywords: 'pokemon' }, { items: [] });
      await cache.set('findItemsAdvanced', { keywords: 'yugioh' }, { items: [] });

      const deleted = await cache.clear();

      expect(deleted).toBe(2);
    });

    it('should return 0 when no entries to clear', async () => {
      const deleted = await cache.clear();

      expect(deleted).toBe(0);
    });
  });

  describe('clearEndpoint', () => {
    it('should clear only specified endpoint', async () => {
      await cache.set('findCompletedItems', { keywords: 'pokemon' }, { items: [] });
      await cache.set('findItemsAdvanced', { keywords: 'yugioh' }, { items: [] });

      const deleted = await cache.clearEndpoint('findCompletedItems');

      expect(deleted).toBe(1);

      const cached1 = await cache.get('findCompletedItems', { keywords: 'pokemon' });
      const cached2 = await cache.get('findItemsAdvanced', { keywords: 'yugioh' });

      expect(cached1).toBeNull();
      expect(cached2).not.toBeNull();
    });
  });

  describe('getStats', () => {
    it('should return cache statistics', async () => {
      await cache.set('findCompletedItems', { keywords: 'pokemon' }, { items: [] });
      await cache.set('findItemsAdvanced', { keywords: 'yugioh' }, { items: [] });

      const stats = await cache.getStats();

      expect(stats.totalKeys).toBe(2);
      expect(stats.memoryUsage).toBe('1.5M');
    });
  });

  describe('isConnected', () => {
    it('should return true when connected', () => {
      expect(cache.isConnected()).toBe(true);
    });
  });
});
