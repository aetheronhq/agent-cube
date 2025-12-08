/**
 * Normalizer Module Tests
 */

import {
  normalizeEbayResponse,
  validateItem,
  filterValidItems
} from '../normalizer';
import { EbayRawResponse, EbayItem, EbaySearchResult } from '../types';

describe('Normalizer Module', () => {
  describe('normalizeEbayResponse', () => {
    it('should normalize a valid findCompletedItems response', () => {
      const rawResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '2',
            item: [
              {
                itemId: ['123456789'],
                title: ['Pokemon Charizard Card'],
                sellingStatus: [{
                  currentPrice: [{
                    __value__: '150.00',
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
                }],
                location: ['United States']
              },
              {
                itemId: ['987654321'],
                title: ['Pokemon Pikachu Card'],
                sellingStatus: [{
                  currentPrice: [{
                    __value__: '25.50',
                    '@currencyId': 'USD'
                  }],
                  sellingState: ['EndedWithSales']
                }],
                listingInfo: [{
                  listingType: ['Auction'],
                  endTime: ['2024-01-02T12:00:00.000Z']
                }],
                condition: [{
                  conditionDisplayName: ['Used']
                }]
              }
            ]
          }],
          paginationOutput: [{
            pageNumber: ['1'],
            entriesPerPage: ['2'],
            totalPages: ['1'],
            totalEntries: ['2']
          }]
        }]
      };

      const result = normalizeEbayResponse(rawResponse, 'findCompletedItems');

      expect(result.items).toHaveLength(2);
      expect(result.totalResults).toBe(2);
      expect(result.pageNumber).toBe(1);
      expect(result.pageSize).toBe(2);

      expect(result.items[0]).toEqual({
        itemId: '123456789',
        title: 'Pokemon Charizard Card',
        price: 150.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date('2024-01-01T12:00:00.000Z'),
        isSold: true,
        location: 'United States'
      });

      expect(result.items[1]).toEqual({
        itemId: '987654321',
        title: 'Pokemon Pikachu Card',
        price: 25.50,
        currency: 'USD',
        condition: 'Used',
        listingType: 'Auction',
        endDate: new Date('2024-01-02T12:00:00.000Z'),
        isSold: true,
        location: undefined
      });
    });

    it('should normalize a valid findItemsAdvanced response', () => {
      const rawResponse: EbayRawResponse = {
        findItemsAdvancedResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '1',
            item: [{
              itemId: ['111222333'],
              title: ['Pokemon Mewtwo Card'],
              sellingStatus: [{
                currentPrice: [{
                  __value__: '75.00',
                  '@currencyId': 'USD'
                }],
                sellingState: ['Active']
              }],
              listingInfo: [{
                listingType: ['FixedPrice'],
                endTime: ['2024-12-31T23:59:59.000Z']
              }],
              condition: [{
                conditionDisplayName: ['Like New']
              }]
            }]
          }],
          paginationOutput: [{
            pageNumber: ['1']
          }]
        }]
      };

      const result = normalizeEbayResponse(rawResponse, 'findItemsAdvanced');

      expect(result.items).toHaveLength(1);
      expect(result.items[0].isSold).toBe(false);
      expect(result.items[0].title).toBe('Pokemon Mewtwo Card');
    });

    it('should return empty result for missing response', () => {
      const rawResponse: EbayRawResponse = {};

      const result = normalizeEbayResponse(rawResponse, 'findCompletedItems');

      expect(result).toEqual({
        items: [],
        totalResults: 0,
        pageNumber: 1,
        pageSize: 0
      });
    });

    it('should return empty result for API failure', () => {
      const rawResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Failure'],
          errorMessage: [{
            error: [{
              message: ['Invalid request']
            }]
          }]
        }]
      };

      const result = normalizeEbayResponse(rawResponse, 'findCompletedItems');

      expect(result).toEqual({
        items: [],
        totalResults: 0,
        pageNumber: 1,
        pageSize: 0
      });
    });

    it('should handle missing optional fields', () => {
      const rawResponse: EbayRawResponse = {
        findCompletedItemsResponse: [{
          ack: ['Success'],
          searchResult: [{
            '@count': '1',
            item: [{
              itemId: ['123'],
              title: ['Minimal Item'],
              sellingStatus: [{}],
              listingInfo: [{}]
            }]
          }]
        }]
      };

      const result = normalizeEbayResponse(rawResponse, 'findCompletedItems');

      expect(result.items).toHaveLength(1);
      expect(result.items[0].price).toBe(0);
      expect(result.items[0].currency).toBe('USD');
      expect(result.items[0].condition).toBe('Unspecified');
      expect(result.items[0].isSold).toBe(false);
    });
  });

  describe('validateItem', () => {
    it('should validate a correct item', () => {
      const item: EbayItem = {
        itemId: '123',
        title: 'Test Item',
        price: 10.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date(),
        isSold: false
      };

      expect(validateItem(item)).toBe(true);
    });

    it('should reject item without itemId', () => {
      const item: EbayItem = {
        itemId: '',
        title: 'Test Item',
        price: 10.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date(),
        isSold: false
      };

      expect(validateItem(item)).toBe(false);
    });

    it('should reject item without title', () => {
      const item: EbayItem = {
        itemId: '123',
        title: '',
        price: 10.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date(),
        isSold: false
      };

      expect(validateItem(item)).toBe(false);
    });

    it('should reject item with negative price', () => {
      const item: EbayItem = {
        itemId: '123',
        title: 'Test Item',
        price: -10.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date(),
        isSold: false
      };

      expect(validateItem(item)).toBe(false);
    });

    it('should reject item with invalid date', () => {
      const item: EbayItem = {
        itemId: '123',
        title: 'Test Item',
        price: 10.00,
        currency: 'USD',
        condition: 'New',
        listingType: 'FixedPrice',
        endDate: new Date('invalid'),
        isSold: false
      };

      expect(validateItem(item)).toBe(false);
    });
  });

  describe('filterValidItems', () => {
    it('should keep all valid items', () => {
      const result: EbaySearchResult = {
        items: [
          {
            itemId: '1',
            title: 'Item 1',
            price: 10,
            currency: 'USD',
            condition: 'New',
            listingType: 'FixedPrice',
            endDate: new Date(),
            isSold: false
          },
          {
            itemId: '2',
            title: 'Item 2',
            price: 20,
            currency: 'USD',
            condition: 'Used',
            listingType: 'Auction',
            endDate: new Date(),
            isSold: true
          }
        ],
        totalResults: 2,
        pageNumber: 1,
        pageSize: 2
      };

      const filtered = filterValidItems(result);

      expect(filtered.items).toHaveLength(2);
      expect(filtered.pageSize).toBe(2);
    });

    it('should filter out invalid items', () => {
      const result: EbaySearchResult = {
        items: [
          {
            itemId: '1',
            title: 'Valid Item',
            price: 10,
            currency: 'USD',
            condition: 'New',
            listingType: 'FixedPrice',
            endDate: new Date(),
            isSold: false
          },
          {
            itemId: '',
            title: 'Invalid Item',
            price: 20,
            currency: 'USD',
            condition: 'Used',
            listingType: 'Auction',
            endDate: new Date(),
            isSold: true
          }
        ],
        totalResults: 2,
        pageNumber: 1,
        pageSize: 2
      };

      const filtered = filterValidItems(result);

      expect(filtered.items).toHaveLength(1);
      expect(filtered.pageSize).toBe(1);
      expect(filtered.items[0].itemId).toBe('1');
    });
  });
});
