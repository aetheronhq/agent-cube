/**
 * Configuration Module Tests
 */

import { getEbayConfig, getRedisUrl, RATE_LIMITS, CACHE_TTL } from '../config';

describe('Configuration Module', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('getEbayConfig', () => {
    it('should return sandbox config by default', () => {
      process.env.EBAY_APP_ID = 'test-app-id';
      process.env.EBAY_CERT_ID = 'test-cert-id';
      process.env.EBAY_DEV_ID = 'test-dev-id';
      delete process.env.EBAY_ENVIRONMENT;

      const config = getEbayConfig();

      expect(config.environment).toBe('sandbox');
      expect(config.baseUrl).toBe('https://svcs.sandbox.ebay.com');
      expect(config.appId).toBe('test-app-id');
      expect(config.certId).toBe('test-cert-id');
      expect(config.devId).toBe('test-dev-id');
    });

    it('should return production config when specified', () => {
      process.env.EBAY_APP_ID = 'test-app-id';
      process.env.EBAY_CERT_ID = 'test-cert-id';
      process.env.EBAY_DEV_ID = 'test-dev-id';
      process.env.EBAY_ENVIRONMENT = 'production';

      const config = getEbayConfig();

      expect(config.environment).toBe('production');
      expect(config.baseUrl).toBe('https://svcs.ebay.com');
    });

    it('should throw error if APP_ID is missing', () => {
      delete process.env.EBAY_APP_ID;
      process.env.EBAY_CERT_ID = 'test-cert-id';
      process.env.EBAY_DEV_ID = 'test-dev-id';

      expect(() => getEbayConfig()).toThrow('EBAY_APP_ID environment variable is required');
    });

    it('should throw error if CERT_ID is missing', () => {
      process.env.EBAY_APP_ID = 'test-app-id';
      delete process.env.EBAY_CERT_ID;
      process.env.EBAY_DEV_ID = 'test-dev-id';

      expect(() => getEbayConfig()).toThrow('EBAY_CERT_ID environment variable is required');
    });

    it('should throw error if DEV_ID is missing', () => {
      process.env.EBAY_APP_ID = 'test-app-id';
      process.env.EBAY_CERT_ID = 'test-cert-id';
      delete process.env.EBAY_DEV_ID;

      expect(() => getEbayConfig()).toThrow('EBAY_DEV_ID environment variable is required');
    });

    it('should throw error for invalid environment', () => {
      process.env.EBAY_APP_ID = 'test-app-id';
      process.env.EBAY_CERT_ID = 'test-cert-id';
      process.env.EBAY_DEV_ID = 'test-dev-id';
      process.env.EBAY_ENVIRONMENT = 'invalid';

      expect(() => getEbayConfig()).toThrow('Invalid EBAY_ENVIRONMENT');
    });
  });

  describe('getRedisUrl', () => {
    it('should return default Redis URL when not specified', () => {
      delete process.env.REDIS_URL;

      const url = getRedisUrl();

      expect(url).toBe('redis://localhost:6379');
    });

    it('should return custom Redis URL when specified', () => {
      process.env.REDIS_URL = 'redis://custom-host:6380';

      const url = getRedisUrl();

      expect(url).toBe('redis://custom-host:6380');
    });
  });

  describe('RATE_LIMITS', () => {
    it('should have correct sandbox limits', () => {
      expect(RATE_LIMITS.sandbox).toEqual({
        reservoir: 5000,
        reservoirRefreshAmount: 5000,
        reservoirRefreshInterval: 24 * 60 * 60 * 1000,
        maxConcurrent: 5,
        minTime: 200
      });
    });

    it('should have correct production limits', () => {
      expect(RATE_LIMITS.production).toEqual({
        reservoir: 5000000,
        reservoirRefreshAmount: 5000000,
        reservoirRefreshInterval: 24 * 60 * 60 * 1000,
        maxConcurrent: 10,
        minTime: 100
      });
    });
  });

  describe('CACHE_TTL', () => {
    it('should be 24 hours in seconds', () => {
      expect(CACHE_TTL).toBe(24 * 60 * 60);
    });
  });
});
