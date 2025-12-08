/**
 * Redis Cache Module
 * 
 * Implements caching layer for eBay API responses using Redis.
 * Reduces API calls and improves performance with 24-hour TTL.
 */

import Redis from 'ioredis';
import crypto from 'crypto';
import { CACHE_TTL } from './config';

/**
 * eBay API response cache using Redis
 */
export class EbayCache {
  private redis: Redis;
  private readonly keyPrefix = 'ebay';

  /**
   * Create a new cache instance
   * 
   * @param redisUrl - Redis connection URL
   */
  constructor(redisUrl: string) {
    this.redis = new Redis(redisUrl, {
      retryStrategy: (times: number) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3
    });

    // Event handlers
    this.redis.on('connect', () => {
      console.log('[Cache] Connected to Redis');
    });

    this.redis.on('error', (error) => {
      console.error('[Cache] Redis error:', error.message);
    });

    this.redis.on('close', () => {
      console.log('[Cache] Redis connection closed');
    });
  }

  /**
   * Generate cache key from endpoint and parameters
   * 
   * @param endpoint - API endpoint name
   * @param params - Query parameters
   * @returns Cache key string
   */
  private generateKey(endpoint: string, params: Record<string, unknown>): string {
    // Sort params to ensure consistent keys
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((acc, key) => {
        acc[key] = params[key];
        return acc;
      }, {} as Record<string, unknown>);

    const paramsHash = crypto
      .createHash('md5')
      .update(JSON.stringify(sortedParams))
      .digest('hex');

    return `${this.keyPrefix}:${endpoint}:${paramsHash}`;
  }

  /**
   * Get cached response
   * 
   * @param endpoint - API endpoint name
   * @param params - Query parameters
   * @returns Cached data or null if not found
   */
  async get<T>(endpoint: string, params: Record<string, unknown>): Promise<T | null> {
    try {
      const key = this.generateKey(endpoint, params);
      const cached = await this.redis.get(key);

      if (cached) {
        console.log(`[Cache] HIT: ${key}`);
        return JSON.parse(cached) as T;
      }

      console.log(`[Cache] MISS: ${key}`);
      return null;
    } catch (error) {
      console.error('[Cache] Get error:', error);
      return null;
    }
  }

  /**
   * Set cached response with TTL
   * 
   * @param endpoint - API endpoint name
   * @param params - Query parameters
   * @param data - Data to cache
   */
  async set(endpoint: string, params: Record<string, unknown>, data: unknown): Promise<void> {
    try {
      const key = this.generateKey(endpoint, params);
      await this.redis.setex(key, CACHE_TTL, JSON.stringify(data));
      console.log(`[Cache] SET: ${key} (TTL: ${CACHE_TTL}s)`);
    } catch (error) {
      console.error('[Cache] Set error:', error);
    }
  }

  /**
   * Clear all eBay cache entries
   * 
   * @returns Number of keys deleted
   */
  async clear(): Promise<number> {
    try {
      const pattern = `${this.keyPrefix}:*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length > 0) {
        const deleted = await this.redis.del(...keys);
        console.log(`[Cache] CLEARED: ${deleted} keys`);
        return deleted;
      }

      console.log('[Cache] CLEARED: No keys found');
      return 0;
    } catch (error) {
      console.error('[Cache] Clear error:', error);
      return 0;
    }
  }

  /**
   * Clear cache for specific endpoint
   * 
   * @param endpoint - API endpoint name
   * @returns Number of keys deleted
   */
  async clearEndpoint(endpoint: string): Promise<number> {
    try {
      const pattern = `${this.keyPrefix}:${endpoint}:*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length > 0) {
        const deleted = await this.redis.del(...keys);
        console.log(`[Cache] CLEARED endpoint ${endpoint}: ${deleted} keys`);
        return deleted;
      }

      console.log(`[Cache] CLEARED endpoint ${endpoint}: No keys found`);
      return 0;
    } catch (error) {
      console.error('[Cache] Clear endpoint error:', error);
      return 0;
    }
  }

  /**
   * Get cache statistics
   * 
   * @returns Cache statistics object
   */
  async getStats(): Promise<{ totalKeys: number; memoryUsage: string }> {
    try {
      const pattern = `${this.keyPrefix}:*`;
      const keys = await this.redis.keys(pattern);
      const info = await this.redis.info('memory');
      
      // Parse memory usage from info string
      const memoryMatch = info.match(/used_memory_human:([^\r\n]+)/);
      const memoryUsage = memoryMatch ? memoryMatch[1] : 'unknown';

      return {
        totalKeys: keys.length,
        memoryUsage
      };
    } catch (error) {
      console.error('[Cache] Stats error:', error);
      return { totalKeys: 0, memoryUsage: 'unknown' };
    }
  }

  /**
   * Check if Redis is connected
   * 
   * @returns True if connected
   */
  isConnected(): boolean {
    return this.redis.status === 'ready';
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    await this.redis.quit();
  }
}
