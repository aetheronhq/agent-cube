/**
 * Client Module Tests
 */

import axios from 'axios';
import { EbayClient } from '../client';
import { EbayRawResponse } from '../types';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock ioredis (same as cache.test.ts)
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

describe('EbayClient', () => {
  const originalEnv = process.env;
  let client: EbayClient;
  let mockAxiosInstance: {
    get: jest.Mock;
  };

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
    process.env.EBAY_APP_ID = 'test-app-id';
    process.env.EBAY_CERT_ID = 'test-cert-id';
    process.env.EBAY_DEV_ID = 'test-dev-id';
    process.env.EBAY_ENVIRONMENT = 'sandbox';

    mockAxiosInstance = {
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    client = new EbayClient('redis://localhost:6379');
  });

  afterEach(async () => {
    await client.close();
    process.env = originalEnv;
  });

  describe('findCompletedItems', () => {
    it('should fetch and return completed items', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '1',
            item: [{
              itemId: ['123'],
              title: ['Test Item'],
              sellingStatus: [{
                currentPrice: [{
                  __value__: '10.00',
                  '@currencyId': 'USD'
                }],
                sellingState: ['EndedWithSales']
              }],
              listingInfo: [{
                listingType: ['FixedPrice'],
                endTime: ['2024-01-01T12:00:00.000Z']
              }],
              condition: [{
                conditionDisplayName: ['New']
              }]
            }]
          }],
          paginationOutput: [{
            pageNumber: ['1']
          }]
        }]
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await client.findCompletedItems({ keywords: 'pokemon' });

      expect(result.items).toHaveLength(1);
      expect(result.items[0].title).toBe('Test Item');
      expect(result.items[0].isSold).toBe(true);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1);
    });

    it('should use cache on second request', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '1',
            item: [{
              itemId: ['123'],
              title: ['Test Item'],
              sellingStatus: [{
                currentPrice: [{
                  __value__: '10.00',
                  '@currencyId': 'USD'
                }],
                sellingState: ['EndedWithSales']
              }],
              listingInfo: [{
                listingType: ['FixedPrice'],
                endTime: ['2024-01-01T12:00:00.000Z']
              }],
              condition: [{
                conditionDisplayName: ['New']
              }]
            }]
          }],
          paginationOutput: [{
            pageNumber: ['1']
          }]
        }]
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      // First request
      await client.findCompletedItems({ keywords: 'pokemon' });
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1);

      // Second request (should use cache)
      const result = await client.findCompletedItems({ keywords: 'pokemon' });
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1); // Still 1, not 2
      expect(result.items).toHaveLength(1);
    });

    it('should force soldItemsOnly to true', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '0'
          }]
        }]
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await client.findCompletedItems({ keywords: 'pokemon', soldItemsOnly: false });

      const callParams = mockAxiosInstance.get.mock.calls[0][1].params;
      expect(callParams['itemFilter(0).name']).toBe('SoldItemsOnly');
      expect(callParams['itemFilter(0).value']).toBe('true');
    });
  });

  describe('findItemsAdvanced', () => {
    it('should fetch and return active items', async () => {
      const mockResponse: EbayRawResponse = {
        findItemsAdvancedResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '1',
            item: [{
              itemId: ['456'],
              title: ['Active Item'],
              sellingStatus: [{
                currentPrice: [{
                  __value__: '20.00',
                  '@currencyId': 'USD'
                }],
                sellingState: ['Active']
              }],
              listingInfo: [{
                listingType: ['Auction'],
                endTime: ['2024-12-31T23:59:59.000Z']
              }],
              condition: [{
                conditionDisplayName: ['Used']
              }]
            }]
          }],
          paginationOutput: [{
            pageNumber: ['1']
          }]
        }]
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await client.findItemsAdvanced({ keywords: 'yugioh' });

      expect(result.items).toHaveLength(1);
      expect(result.items[0].title).toBe('Active Item');
      expect(result.items[0].isSold).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should retry on server error', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '0'
          }]
        }]
      };

      mockAxiosInstance.get
        .mockRejectedValueOnce({ response: { status: 500 }, message: 'Server error' })
        .mockRejectedValueOnce({ response: { status: 503 }, message: 'Service unavailable' })
        .mockResolvedValueOnce({ data: mockResponse });

      const result = await client.findCompletedItems({ keywords: 'pokemon' });

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(3);
      expect(result.items).toHaveLength(0);
    }, 15000);

    it('should not retry on client error', async () => {
      mockAxiosInstance.get.mockRejectedValue({
        response: { status: 400 },
        message: 'Bad request'
      });

      await expect(
        client.findCompletedItems({ keywords: 'pokemon' })
      ).rejects.toThrow('eBay API client error');

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1);
    });

    it('should retry on 429 rate limit error', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '0'
          }]
        }]
      };

      mockAxiosInstance.get
        .mockRejectedValueOnce({ response: { status: 429 }, message: 'Rate limited' })
        .mockResolvedValueOnce({ data: mockResponse });

      const result = await client.findCompletedItems({ keywords: 'pokemon' });

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
      expect(result.items).toHaveLength(0);
    });

    it('should fail after max retries', async () => {
      mockAxiosInstance.get.mockRejectedValue({
        response: { status: 500 },
        message: 'Server error'
      });

      await expect(
        client.findCompletedItems({ keywords: 'pokemon' })
      ).rejects.toThrow('eBay API request failed after 3 attempts');

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(3);
    }, 15000);
  });

  describe('request parameters', () => {
    it('should build correct parameters with filters', async () => {
      const mockResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '0'
          }]
        }]
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await client.findCompletedItems({
        keywords: 'pokemon',
        minPrice: 10,
        maxPrice: 100,
        condition: 'New',
        categoryId: '12345'
      });

      const callParams = mockAxiosInstance.get.mock.calls[0][1].params;

      expect(callParams['OPERATION-NAME']).toBe('findCompletedItems');
      expect(callParams['keywords']).toBe('pokemon');
      expect(callParams['categoryId']).toBe('12345');
      expect(callParams['itemFilter(0).name']).toBe('SoldItemsOnly');
      expect(callParams['itemFilter(1).name']).toBe('MinPrice');
      expect(callParams['itemFilter(1).value']).toBe('10');
      expect(callParams['itemFilter(2).name']).toBe('MaxPrice');
      expect(callParams['itemFilter(2).value']).toBe('100');
      expect(callParams['itemFilter(3).name']).toBe('Condition');
      expect(callParams['itemFilter(3).value']).toBe('New');
    });
  });

  describe('cache management', () => {
    it('should clear cache', async () => {
      const deleted = await client.clearCache();
      expect(typeof deleted).toBe('number');
    });

    it('should get cache stats', async () => {
      const stats = await client.getCacheStats();
      expect(stats).toHaveProperty('totalKeys');
      expect(stats).toHaveProperty('memoryUsage');
    });

    it('should check cache connection', () => {
      const connected = client.isCacheConnected();
      expect(typeof connected).toBe('boolean');
    });
  });
});
