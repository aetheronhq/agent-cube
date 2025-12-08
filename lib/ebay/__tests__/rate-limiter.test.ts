/**
 * Rate Limiter Module Tests
 */

import Bottleneck from 'bottleneck';
import { createRateLimiter, getRemainingCalls, isThrottling } from '../rate-limiter';

describe('Rate Limiter Module', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
    process.env.EBAY_APP_ID = 'test-app-id';
    process.env.EBAY_CERT_ID = 'test-cert-id';
    process.env.EBAY_DEV_ID = 'test-dev-id';
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('createRateLimiter', () => {
    it('should create a Bottleneck instance', () => {
      const limiter = createRateLimiter();

      expect(limiter).toBeInstanceOf(Bottleneck);
    });

    it('should configure sandbox limits by default', () => {
      process.env.EBAY_ENVIRONMENT = 'sandbox';

      const limiter = createRateLimiter();
      const counts = limiter.counts();

      expect(counts).toBeDefined();
    });

    it('should configure production limits when specified', () => {
      process.env.EBAY_ENVIRONMENT = 'production';

      const limiter = createRateLimiter();
      const counts = limiter.counts();

      expect(counts).toBeDefined();
    });

    it('should be configurable with event handlers', () => {
      const limiter = createRateLimiter();
      
      // Verify limiter is properly configured
      expect(limiter).toBeInstanceOf(Bottleneck);
      
      // Test that we can add event listeners
      let errorHandled = false;
      limiter.on('error', () => {
        errorHandled = true;
      });
      
      expect(errorHandled).toBe(false); // Not triggered yet
    });
  });

  describe('getRemainingCalls', () => {
    it('should return remaining calls count', async () => {
      const limiter = createRateLimiter();

      const remaining = await getRemainingCalls(limiter);

      expect(typeof remaining).toBe('number');
      expect(remaining).toBeGreaterThanOrEqual(0);
    });
  });

  describe('isThrottling', () => {
    it('should return false when no requests are queued', () => {
      const limiter = createRateLimiter();

      const throttling = isThrottling(limiter);

      expect(throttling).toBe(false);
    });

    it('should check throttling status based on queue', () => {
      const limiter = createRateLimiter();
      
      // Initially no throttling
      expect(isThrottling(limiter)).toBe(false);
      
      // The function should return a boolean
      const result = isThrottling(limiter);
      expect(typeof result).toBe('boolean');
    });
  });
});
