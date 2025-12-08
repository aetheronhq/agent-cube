/**
 * Index Module Tests
 * 
 * Tests for main exports
 */

import * as EbayModule from '../index';

describe('Index Module', () => {
  it('should export EbayClient', () => {
    expect(EbayModule.EbayClient).toBeDefined();
    expect(typeof EbayModule.EbayClient).toBe('function');
  });

  it('should export EbayCache', () => {
    expect(EbayModule.EbayCache).toBeDefined();
    expect(typeof EbayModule.EbayCache).toBe('function');
  });

  it('should export rate limiter functions', () => {
    expect(EbayModule.createRateLimiter).toBeDefined();
    expect(typeof EbayModule.createRateLimiter).toBe('function');
    
    expect(EbayModule.getRemainingCalls).toBeDefined();
    expect(typeof EbayModule.getRemainingCalls).toBe('function');
    
    expect(EbayModule.isThrottling).toBeDefined();
    expect(typeof EbayModule.isThrottling).toBe('function');
  });

  it('should export normalizer functions', () => {
    expect(EbayModule.normalizeEbayResponse).toBeDefined();
    expect(typeof EbayModule.normalizeEbayResponse).toBe('function');
    
    expect(EbayModule.validateItem).toBeDefined();
    expect(typeof EbayModule.validateItem).toBe('function');
    
    expect(EbayModule.filterValidItems).toBeDefined();
    expect(typeof EbayModule.filterValidItems).toBe('function');
  });

  it('should export config functions', () => {
    expect(EbayModule.getEbayConfig).toBeDefined();
    expect(typeof EbayModule.getEbayConfig).toBe('function');
    
    expect(EbayModule.getRedisUrl).toBeDefined();
    expect(typeof EbayModule.getRedisUrl).toBe('function');
  });

  it('should export constants', () => {
    expect(EbayModule.RATE_LIMITS).toBeDefined();
    expect(typeof EbayModule.RATE_LIMITS).toBe('object');
    
    expect(EbayModule.CACHE_TTL).toBeDefined();
    expect(typeof EbayModule.CACHE_TTL).toBe('number');
  });
});
