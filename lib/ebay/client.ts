/**
 * eBay API Client
 * 
 * Main client for interacting with eBay Finding API.
 * Includes rate limiting, caching, error handling, and retry logic.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import Bottleneck from 'bottleneck';
import { EbayCache } from './cache';
import { getEbayConfig, getRedisUrl } from './config';
import { createRateLimiter } from './rate-limiter';
import { normalizeEbayResponse, filterValidItems } from './normalizer';
import { EbaySearchParams, EbaySearchResult, EbayRawResponse } from './types';

/**
 * eBay API Client with rate limiting and caching
 */
export class EbayClient {
  private config = getEbayConfig();
  private rateLimiter: Bottleneck;
  private cache: EbayCache;
  private httpClient: AxiosInstance;

  /**
   * Create a new eBay API client
   * 
   * @param redisUrl - Optional Redis URL (defaults to env var or localhost)
   */
  constructor(redisUrl?: string) {
    this.rateLimiter = createRateLimiter();
    this.cache = new EbayCache(redisUrl || getRedisUrl());
    this.httpClient = axios.create({
      baseURL: this.config.baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log(`[EbayClient] Initialized for ${this.config.environment} environment`);
  }

  /**
   * Search for completed (sold) items
   * 
   * @param params - Search parameters
   * @returns Search results with sold items
   */
  async findCompletedItems(params: EbaySearchParams): Promise<EbaySearchResult> {
    // Ensure soldItemsOnly is set for this operation
    const searchParams = { ...params, soldItemsOnly: true };

    // Check cache first
    const cached = await this.cache.get<EbaySearchResult>('findCompletedItems', searchParams);
    if (cached) {
      return cached;
    }

    // Make rate-limited API call
    const response = await this.rateLimiter.schedule(() =>
      this.makeRequest('findCompletedItems', searchParams)
    );

    const normalized = normalizeEbayResponse(response, 'findCompletedItems');
    const filtered = filterValidItems(normalized);

    // Cache the result
    await this.cache.set('findCompletedItems', searchParams, filtered);

    return filtered;
  }

  /**
   * Search for active items
   * 
   * @param params - Search parameters
   * @returns Search results with active items
   */
  async findItemsAdvanced(params: EbaySearchParams): Promise<EbaySearchResult> {
    // Check cache first
    const cached = await this.cache.get<EbaySearchResult>('findItemsAdvanced', params);
    if (cached) {
      return cached;
    }

    // Make rate-limited API call
    const response = await this.rateLimiter.schedule(() =>
      this.makeRequest('findItemsAdvanced', params)
    );

    const normalized = normalizeEbayResponse(response, 'findItemsAdvanced');
    const filtered = filterValidItems(normalized);

    // Cache the result
    await this.cache.set('findItemsAdvanced', params, filtered);

    return filtered;
  }

  /**
   * Make HTTP request to eBay API with retry logic
   * 
   * @param operation - API operation name
   * @param params - Search parameters
   * @param attempt - Current attempt number (for retry logic)
   * @returns Raw API response
   */
  private async makeRequest(
    operation: string,
    params: EbaySearchParams,
    attempt = 1
  ): Promise<EbayRawResponse> {
    const maxAttempts = 3;

    try {
      const requestParams = this.buildRequestParams(operation, params);
      
      console.log(`[EbayClient] ${operation} request (attempt ${attempt}/${maxAttempts}):`, {
        keywords: params.keywords,
        filters: Object.keys(params).filter(k => k !== 'keywords' && params[k as keyof EbaySearchParams])
      });

      const response = await this.httpClient.get('/services/search/FindingService/v1', {
        params: requestParams
      });

      return response.data as EbayRawResponse;
    } catch (error) {
      return this.handleRequestError(error, operation, params, attempt, maxAttempts);
    }
  }

  /**
   * Handle request errors with retry logic
   * 
   * @param error - Error object
   * @param operation - API operation name
   * @param params - Search parameters
   * @param attempt - Current attempt number
   * @param maxAttempts - Maximum number of attempts
   * @returns Raw API response (if retry succeeds)
   * @throws Error if all retries fail
   */
  private async handleRequestError(
    error: unknown,
    operation: string,
    params: EbaySearchParams,
    attempt: number,
    maxAttempts: number
  ): Promise<EbayRawResponse> {
    const axiosError = error as AxiosError;

    // Log error details
    console.error(`[EbayClient] Request failed (attempt ${attempt}/${maxAttempts}):`, {
      status: axiosError.response?.status,
      message: axiosError.message,
      operation
    });

    // Don't retry on client errors (except 429 rate limiting)
    if (axiosError.response?.status && 
        axiosError.response.status >= 400 && 
        axiosError.response.status < 500 && 
        axiosError.response.status !== 429) {
      throw new Error(
        `eBay API client error (${axiosError.response.status}): ${axiosError.message}`
      );
    }

    // Retry on server errors or rate limiting
    if (attempt < maxAttempts) {
      const delay = Math.pow(2, attempt) * 1000; // Exponential backoff: 2s, 4s, 8s
      console.warn(`[EbayClient] Retrying in ${delay}ms...`);
      await this.sleep(delay);
      return this.makeRequest(operation, params, attempt + 1);
    }

    // All retries exhausted
    throw new Error(
      `eBay API request failed after ${maxAttempts} attempts: ${axiosError.message}`
    );
  }

  /**
   * Build eBay API request parameters
   * 
   * @param operation - API operation name
   * @param params - Search parameters
   * @returns URL query parameters
   */
  private buildRequestParams(
    operation: string,
    params: EbaySearchParams
  ): Record<string, string> {
    const baseParams: Record<string, string> = {
      'OPERATION-NAME': operation,
      'SERVICE-VERSION': '1.0.0',
      'SECURITY-APPNAME': this.config.appId,
      'RESPONSE-DATA-FORMAT': 'JSON',
      'keywords': params.keywords
    };

    // Add pagination
    if (params.pageNumber) {
      baseParams['paginationInput.pageNumber'] = params.pageNumber.toString();
    }
    if (params.pageSize) {
      baseParams['paginationInput.entriesPerPage'] = params.pageSize.toString();
    }

    // Add category filter
    if (params.categoryId) {
      baseParams['categoryId'] = params.categoryId;
    }

    // Build item filters
    const filters: Record<string, string> = {};
    let filterIndex = 0;

    if (params.soldItemsOnly) {
      filters[`itemFilter(${filterIndex}).name`] = 'SoldItemsOnly';
      filters[`itemFilter(${filterIndex}).value`] = 'true';
      filterIndex++;
    }

    if (params.minPrice !== undefined) {
      filters[`itemFilter(${filterIndex}).name`] = 'MinPrice';
      filters[`itemFilter(${filterIndex}).value`] = params.minPrice.toString();
      filterIndex++;
    }

    if (params.maxPrice !== undefined) {
      filters[`itemFilter(${filterIndex}).name`] = 'MaxPrice';
      filters[`itemFilter(${filterIndex}).value`] = params.maxPrice.toString();
      filterIndex++;
    }

    if (params.condition) {
      filters[`itemFilter(${filterIndex}).name`] = 'Condition';
      filters[`itemFilter(${filterIndex}).value`] = params.condition;
    }

    return { ...baseParams, ...filters };
  }

  /**
   * Utility: sleep for specified milliseconds
   * 
   * @param ms - Milliseconds to sleep
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear all cached responses
   * 
   * @returns Number of cache entries cleared
   */
  async clearCache(): Promise<number> {
    return this.cache.clear();
  }

  /**
   * Get cache statistics
   * 
   * @returns Cache statistics
   */
  async getCacheStats(): Promise<{ totalKeys: number; memoryUsage: string }> {
    return this.cache.getStats();
  }

  /**
   * Check if cache is connected
   * 
   * @returns True if cache is connected
   */
  isCacheConnected(): boolean {
    return this.cache.isConnected();
  }

  /**
   * Close all connections (rate limiter and cache)
   */
  async close(): Promise<void> {
    console.log('[EbayClient] Closing connections...');
    await this.cache.close();
    await this.rateLimiter.stop();
    console.log('[EbayClient] Connections closed');
  }
}
