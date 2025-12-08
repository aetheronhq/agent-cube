/**
 * Response Normalizer Module
 * 
 * Transforms raw eBay API responses into normalized, type-safe data structures.
 * Handles missing fields, type conversions, and data validation.
 */

import {
  EbayItem,
  EbaySearchResult,
  EbayRawResponse,
  EbayRawItem
} from './types';

/**
 * Normalize eBay API response to internal format
 * 
 * @param response - Raw eBay API response
 * @param operation - API operation name (for selecting correct response path)
 * @returns Normalized search result
 */
export function normalizeEbayResponse(
  response: EbayRawResponse,
  operation: 'findCompletedItems' | 'findItemsAdvanced'
): EbaySearchResult {
  // Select the appropriate response path based on operation
  const responseKey = operation === 'findCompletedItems' 
    ? 'findCompletedItemsResponse' 
    : 'findItemsAdvancedResponse';

  const findResponse = response[responseKey]?.[0];

  if (!findResponse) {
    return createEmptyResult();
  }

  // Check for API errors
  if (findResponse.ack?.[0] === 'Failure') {
    const errorMessage = findResponse.errorMessage?.[0]?.error?.[0]?.message?.[0] || 'Unknown error';
    console.error(`[Normalizer] API returned error: ${errorMessage}`);
    return createEmptyResult();
  }

  const searchResult = findResponse.searchResult?.[0];

  if (!searchResult) {
    return createEmptyResult();
  }

  const items = (searchResult.item || []).map(normalizeItem);
  const paginationOutput = findResponse.paginationOutput?.[0];

  return {
    items,
    totalResults: parseInt(searchResult['@count'] || '0', 10),
    pageNumber: parseInt(paginationOutput?.pageNumber?.[0] || '1', 10),
    pageSize: items.length
  };
}

/**
 * Normalize individual eBay item
 * 
 * @param item - Raw eBay item data
 * @returns Normalized item
 */
function normalizeItem(item: EbayRawItem): EbayItem {
  const sellingStatus = item.sellingStatus?.[0];
  const listingInfo = item.listingInfo?.[0];
  const condition = item.condition?.[0];

  // Extract price
  const priceValue = sellingStatus?.currentPrice?.[0]?.__value__ || 
                     sellingStatus?.convertedCurrentPrice?.[0]?.__value__ || 
                     '0';
  const price = parseFloat(priceValue);

  // Extract currency
  const currency = sellingStatus?.currentPrice?.[0]?.['@currencyId'] || 
                   sellingStatus?.convertedCurrentPrice?.[0]?.['@currencyId'] || 
                   'USD';

  // Determine listing type
  const listingTypeRaw = listingInfo?.listingType?.[0] || '';
  const listingType: 'Auction' | 'FixedPrice' = 
    listingTypeRaw === 'Auction' || listingTypeRaw === 'AuctionWithBIN' 
      ? 'Auction' 
      : 'FixedPrice';

  // Parse end date
  const endTimeStr = listingInfo?.endTime?.[0];
  const endDate = endTimeStr ? new Date(endTimeStr) : new Date();

  // Check if item is sold
  const sellingState = sellingStatus?.sellingState?.[0] || '';
  const isSold = sellingState === 'EndedWithSales';

  return {
    itemId: item.itemId?.[0] || '',
    title: item.title?.[0] || '',
    price,
    currency,
    condition: condition?.conditionDisplayName?.[0] || 'Unspecified',
    listingType,
    endDate,
    isSold,
    location: item.location?.[0]
  };
}

/**
 * Create an empty search result
 * 
 * @returns Empty search result
 */
function createEmptyResult(): EbaySearchResult {
  return {
    items: [],
    totalResults: 0,
    pageNumber: 1,
    pageSize: 0
  };
}

/**
 * Validate normalized item
 * 
 * @param item - Normalized item to validate
 * @returns True if item is valid
 */
export function validateItem(item: EbayItem): boolean {
  // Required fields
  if (!item.itemId || !item.title) {
    return false;
  }

  // Price should be non-negative
  if (item.price < 0) {
    return false;
  }

  // Date should be valid
  if (!(item.endDate instanceof Date) || isNaN(item.endDate.getTime())) {
    return false;
  }

  return true;
}

/**
 * Filter out invalid items from search results
 * 
 * @param result - Search result to filter
 * @returns Filtered search result
 */
export function filterValidItems(result: EbaySearchResult): EbaySearchResult {
  const validItems = result.items.filter(validateItem);
  
  if (validItems.length < result.items.length) {
    console.warn(`[Normalizer] Filtered out ${result.items.length - validItems.length} invalid items`);
  }

  return {
    ...result,
    items: validItems,
    pageSize: validItems.length
  };
}
