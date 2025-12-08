/**
 * Rate Limiter Module
 * 
 * Implements rate limiting using Bottleneck to prevent API quota exhaustion.
 * Supports both sandbox (5K/day) and production (5M/day) environments.
 */

import Bottleneck from 'bottleneck';
import { getEbayConfig, RATE_LIMITS } from './config';

/**
 * Create a rate limiter configured for the current environment
 * 
 * @returns Configured Bottleneck rate limiter instance
 */
export function createRateLimiter(): Bottleneck {
  const config = getEbayConfig();
  const limits = RATE_LIMITS[config.environment];

  const limiter = new Bottleneck({
    reservoir: limits.reservoir,
    reservoirRefreshAmount: limits.reservoirRefreshAmount,
    reservoirRefreshInterval: limits.reservoirRefreshInterval,
    maxConcurrent: limits.maxConcurrent,
    minTime: limits.minTime
  });

  // Event handlers for monitoring
  limiter.on('depleted', () => {
    console.warn(`[RateLimiter] Reservoir depleted for ${config.environment} environment. Requests will be throttled.`);
  });

  limiter.on('error', (error) => {
    console.error('[RateLimiter] Error:', error);
  });

  limiter.on('debug', (message) => {
    if (process.env.DEBUG === 'true') {
      console.debug('[RateLimiter] Debug:', message);
    }
  });

  console.log(`[RateLimiter] Initialized for ${config.environment} environment:`, {
    dailyLimit: limits.reservoir,
    maxConcurrent: limits.maxConcurrent,
    minTimeBetweenRequests: `${limits.minTime}ms`
  });

  return limiter;
}

/**
 * Get current reservoir level (remaining API calls)
 * 
 * @param limiter - Bottleneck instance
 * @returns Number of remaining API calls in reservoir
 */
export async function getRemainingCalls(limiter: Bottleneck): Promise<number> {
  const counts = limiter.counts();
  return (counts.RECEIVED || 0) - (counts.DONE || 0);
}

/**
 * Check if rate limiter is currently throttling requests
 * 
 * @param limiter - Bottleneck instance
 * @returns True if requests are being throttled
 */
export function isThrottling(limiter: Bottleneck): boolean {
  const counts = limiter.counts();
  return counts.QUEUED > 0;
}
