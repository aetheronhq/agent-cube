/**
 * eBay API Configuration Module
 * 
 * Handles environment variables, API configuration, and rate limiting settings.
 */

import { config as loadEnv } from 'dotenv';
import { EbayConfig, RateLimitConfig } from './types';

// Load environment variables
loadEnv();

/**
 * Get eBay API configuration from environment variables
 * 
 * @returns eBay configuration object
 * @throws Error if required environment variables are missing
 */
export function getEbayConfig(): EbayConfig {
  const environment = (process.env.EBAY_ENVIRONMENT || 'sandbox') as 'sandbox' | 'production';
  
  // Validate environment value
  if (environment !== 'sandbox' && environment !== 'production') {
    throw new Error(`Invalid EBAY_ENVIRONMENT: ${environment}. Must be 'sandbox' or 'production'.`);
  }

  const baseUrls = {
    sandbox: 'https://svcs.sandbox.ebay.com',
    production: 'https://svcs.ebay.com'
  };

  const config: EbayConfig = {
    appId: process.env.EBAY_APP_ID || '',
    certId: process.env.EBAY_CERT_ID || '',
    devId: process.env.EBAY_DEV_ID || '',
    environment,
    baseUrl: baseUrls[environment]
  };

  // Validate required fields
  if (!config.appId) {
    throw new Error('EBAY_APP_ID environment variable is required');
  }
  if (!config.certId) {
    throw new Error('EBAY_CERT_ID environment variable is required');
  }
  if (!config.devId) {
    throw new Error('EBAY_DEV_ID environment variable is required');
  }

  return config;
}

/**
 * Rate limiting configurations for sandbox and production environments
 * 
 * Sandbox: 5,000 calls/day, 5 concurrent, 200ms min time
 * Production: 5,000,000 calls/day, 10 concurrent, 100ms min time
 */
export const RATE_LIMITS: Record<'sandbox' | 'production', RateLimitConfig> = {
  sandbox: {
    reservoir: 5000,
    reservoirRefreshAmount: 5000,
    reservoirRefreshInterval: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
    maxConcurrent: 5,
    minTime: 200 // 200ms between requests
  },
  production: {
    reservoir: 5000000,
    reservoirRefreshAmount: 5000000,
    reservoirRefreshInterval: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
    maxConcurrent: 10,
    minTime: 100 // 100ms between requests
  }
};

/**
 * Cache TTL in seconds (24 hours)
 */
export const CACHE_TTL = 24 * 60 * 60;

/**
 * Default Redis URL
 */
export const DEFAULT_REDIS_URL = 'redis://localhost:6379';

/**
 * Get Redis URL from environment or use default
 */
export function getRedisUrl(): string {
  return process.env.REDIS_URL || DEFAULT_REDIS_URL;
}
