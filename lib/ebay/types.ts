/**
 * eBay API Integration Types
 * 
 * Type definitions for eBay API client, configuration, and data models.
 */

/**
 * eBay API configuration
 */
export interface EbayConfig {
  appId: string;
  certId: string;
  devId: string;
  environment: 'sandbox' | 'production';
  baseUrl: string;
}

/**
 * Search parameters for eBay API queries
 */
export interface EbaySearchParams extends Record<string, unknown> {
  keywords: string;
  categoryId?: string;
  minPrice?: number;
  maxPrice?: number;
  condition?: 'New' | 'Used' | 'Unspecified';
  soldItemsOnly?: boolean;
  pageNumber?: number;
  pageSize?: number;
}

/**
 * Normalized eBay item representation
 */
export interface EbayItem {
  itemId: string;
  title: string;
  price: number;
  currency: string;
  condition: string;
  listingType: 'Auction' | 'FixedPrice';
  endDate: Date;
  isSold: boolean;
  location?: string;
}

/**
 * Search result containing items and pagination info
 */
export interface EbaySearchResult {
  items: EbayItem[];
  totalResults: number;
  pageNumber: number;
  pageSize: number;
}

/**
 * Rate limiting configuration
 */
export interface RateLimitConfig {
  reservoir: number;
  reservoirRefreshAmount: number;
  reservoirRefreshInterval: number;
  maxConcurrent: number;
  minTime: number;
}

/**
 * Raw eBay API response types (for internal parsing)
 */
export interface EbayRawResponse {
  findCompletedItemsResponse?: EbayRawFindResponse[];
  findItemsAdvancedResponse?: EbayRawFindResponse[];
}

export interface EbayRawFindResponse {
  searchResult?: EbayRawSearchResult[];
  paginationOutput?: EbayRawPaginationOutput[];
  ack?: string[];
  errorMessage?: EbayRawErrorMessage[];
}

export interface EbayRawSearchResult {
  '@count'?: string;
  item?: EbayRawItem[];
}

export interface EbayRawPaginationOutput {
  pageNumber?: string[];
  entriesPerPage?: string[];
  totalPages?: string[];
  totalEntries?: string[];
}

export interface EbayRawItem {
  itemId?: string[];
  title?: string[];
  globalId?: string[];
  country?: string[];
  location?: string[];
  sellingStatus?: EbayRawSellingStatus[];
  listingInfo?: EbayRawListingInfo[];
  condition?: EbayRawCondition[];
  shippingInfo?: EbayRawShippingInfo[];
}

export interface EbayRawSellingStatus {
  currentPrice?: EbayRawPrice[];
  convertedCurrentPrice?: EbayRawPrice[];
  sellingState?: string[];
  timeLeft?: string[];
}

export interface EbayRawPrice {
  __value__?: string;
  '@currencyId'?: string;
}

export interface EbayRawListingInfo {
  listingType?: string[];
  startTime?: string[];
  endTime?: string[];
  buyItNowAvailable?: string[];
}

export interface EbayRawCondition {
  conditionId?: string[];
  conditionDisplayName?: string[];
}

export interface EbayRawShippingInfo {
  shippingType?: string[];
  shipToLocations?: string[];
}

export interface EbayRawErrorMessage {
  error?: EbayRawError[];
}

export interface EbayRawError {
  errorId?: string[];
  domain?: string[];
  severity?: string[];
  category?: string[];
  message?: string[];
}
