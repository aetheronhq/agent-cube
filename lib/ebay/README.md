# eBay API Integration

Production-ready eBay API client with rate limiting and caching for CardTrail PTCG Price Tracker.

## Features

- ✅ **Complete eBay Finding API Support** - Search completed and active listings
- ✅ **Rate Limiting** - Bottleneck-based rate limiting (5K/day sandbox, 5M/day production)
- ✅ **Redis Caching** - 24-hour TTL cache to minimize API calls
- ✅ **Error Handling** - Exponential backoff retry logic with comprehensive error handling
- ✅ **Type Safety** - Full TypeScript support with strict mode
- ✅ **Test Coverage** - 90%+ code coverage with comprehensive unit and integration tests

## Installation

```bash
npm install axios bottleneck ioredis dotenv
```

## Configuration

Create a `.env` file with your eBay API credentials:

```env
# eBay API Credentials
EBAY_APP_ID=your_app_id_here
EBAY_CERT_ID=your_cert_id_here
EBAY_DEV_ID=your_dev_id_here

# Environment (sandbox | production)
EBAY_ENVIRONMENT=sandbox

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### Getting eBay API Credentials

1. Sign up for an eBay Developer account at https://developer.ebay.com
2. Create an application to get your App ID, Cert ID, and Dev ID
3. Use sandbox credentials for testing, production credentials for live deployment

## Quick Start

```typescript
import { EbayClient } from './lib/ebay';

async function main() {
  // Create client instance
  const client = new EbayClient();

  try {
    // Search for completed (sold) Pokemon cards
    const results = await client.findCompletedItems({
      keywords: 'Pokemon Charizard',
      soldItemsOnly: true,
      minPrice: 10,
      maxPrice: 500,
      condition: 'New'
    });

    console.log(`Found ${results.totalResults} sold items`);
    
    results.items.forEach(item => {
      console.log(`${item.title}: $${item.price} ${item.currency}`);
      console.log(`  Condition: ${item.condition}`);
      console.log(`  Sold: ${item.isSold ? 'Yes' : 'No'}`);
      console.log(`  End Date: ${item.endDate}`);
    });
  } finally {
    // Always close connections when done
    await client.close();
  }
}

main();
```

## API Reference

### EbayClient

Main client for interacting with eBay API.

#### Constructor

```typescript
constructor(redisUrl?: string)
```

Creates a new eBay API client instance.

**Parameters:**
- `redisUrl` (optional): Redis connection URL. Defaults to `REDIS_URL` environment variable or `redis://localhost:6379`

#### Methods

##### `findCompletedItems(params: EbaySearchParams): Promise<EbaySearchResult>`

Search for completed (sold) items.

**Parameters:**
```typescript
interface EbaySearchParams {
  keywords: string;           // Search keywords (required)
  categoryId?: string;        // eBay category ID
  minPrice?: number;          // Minimum price filter
  maxPrice?: number;          // Maximum price filter
  condition?: 'New' | 'Used' | 'Unspecified';
  soldItemsOnly?: boolean;    // Filter to sold items only
  pageNumber?: number;        // Page number for pagination
  pageSize?: number;          // Items per page
}
```

**Returns:**
```typescript
interface EbaySearchResult {
  items: EbayItem[];          // Array of items
  totalResults: number;       // Total number of results
  pageNumber: number;         // Current page number
  pageSize: number;           // Number of items in current page
}

interface EbayItem {
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
```

**Example:**
```typescript
const results = await client.findCompletedItems({
  keywords: 'Pokemon Charizard',
  minPrice: 50,
  maxPrice: 200,
  condition: 'New'
});
```

##### `findItemsAdvanced(params: EbaySearchParams): Promise<EbaySearchResult>`

Search for active (currently listed) items.

**Parameters:** Same as `findCompletedItems`

**Returns:** Same as `findCompletedItems`

**Example:**
```typescript
const results = await client.findItemsAdvanced({
  keywords: 'Pokemon Pikachu',
  categoryId: '183454'  // Trading Card Games category
});
```

##### `clearCache(): Promise<number>`

Clear all cached eBay API responses.

**Returns:** Number of cache entries cleared

**Example:**
```typescript
const cleared = await client.clearCache();
console.log(`Cleared ${cleared} cache entries`);
```

##### `getCacheStats(): Promise<{ totalKeys: number; memoryUsage: string }>`

Get cache statistics.

**Returns:** Object with total keys and memory usage

**Example:**
```typescript
const stats = await client.getCacheStats();
console.log(`Cache has ${stats.totalKeys} keys using ${stats.memoryUsage}`);
```

##### `isCacheConnected(): boolean`

Check if Redis cache is connected.

**Returns:** `true` if connected, `false` otherwise

##### `close(): Promise<void>`

Close all connections (Redis and rate limiter). Always call this when done.

**Example:**
```typescript
await client.close();
```

## Rate Limiting

The client automatically handles rate limiting based on your environment:

### Sandbox Environment
- **Daily Limit:** 5,000 API calls
- **Max Concurrent:** 5 requests
- **Min Time Between Requests:** 200ms

### Production Environment
- **Daily Limit:** 5,000,000 API calls
- **Max Concurrent:** 10 requests
- **Min Time Between Requests:** 100ms

Rate limiting is handled transparently by the Bottleneck library. Requests are automatically queued when limits are reached.

## Caching

All API responses are cached in Redis with a 24-hour TTL (Time To Live). This significantly reduces API calls and improves performance.

### Cache Key Format

```
ebay:{endpoint}:{md5(params)}
```

Example: `ebay:findCompletedItems:a1b2c3d4e5f6...`

### Cache Behavior

1. **Cache Hit:** Returns cached data immediately (no API call)
2. **Cache Miss:** Makes API call, caches result, returns data
3. **Cache Expiry:** After 24 hours, data is automatically removed

### Manual Cache Management

```typescript
// Clear all cache
await client.clearCache();

// Get cache statistics
const stats = await client.getCacheStats();
console.log(`Total keys: ${stats.totalKeys}`);
console.log(`Memory usage: ${stats.memoryUsage}`);
```

## Error Handling

The client implements comprehensive error handling with exponential backoff retry logic.

### Retry Behavior

- **Server Errors (5xx):** Retries up to 3 times with exponential backoff (2s, 4s, 8s)
- **Rate Limiting (429):** Retries up to 3 times with exponential backoff
- **Client Errors (4xx):** No retry (except 429)
- **Network Errors:** Retries up to 3 times

### Error Examples

```typescript
try {
  const results = await client.findCompletedItems({
    keywords: 'Pokemon'
  });
} catch (error) {
  if (error.message.includes('client error')) {
    // Handle client error (bad request, invalid params, etc.)
    console.error('Invalid request:', error.message);
  } else if (error.message.includes('failed after 3 attempts')) {
    // Handle retry exhaustion
    console.error('API unavailable:', error.message);
  } else {
    // Handle other errors
    console.error('Unexpected error:', error.message);
  }
}
```

## Advanced Usage

### Custom Redis Configuration

```typescript
const client = new EbayClient('redis://custom-host:6380/1');
```

### Pagination

```typescript
async function getAllResults(keywords: string) {
  const client = new EbayClient();
  const allItems = [];
  let pageNumber = 1;
  const pageSize = 100;

  try {
    while (true) {
      const results = await client.findCompletedItems({
        keywords,
        pageNumber,
        pageSize
      });

      allItems.push(...results.items);

      if (results.items.length < pageSize) {
        break; // No more pages
      }

      pageNumber++;
    }

    return allItems;
  } finally {
    await client.close();
  }
}
```

### Filtering Results

```typescript
const results = await client.findCompletedItems({
  keywords: 'Pokemon Charizard',
  minPrice: 100,
  maxPrice: 500,
  condition: 'New',
  soldItemsOnly: true
});

// Filter by location
const usItems = results.items.filter(item => 
  item.location?.includes('United States')
);

// Filter by listing type
const auctionItems = results.items.filter(item => 
  item.listingType === 'Auction'
);
```

## Testing

### Run All Tests

```bash
npm test
```

### Run Tests with Coverage

```bash
npm run test:coverage
```

### Run Type Checking

```bash
npm run typecheck
```

### Run Linting

```bash
npm run lint
```

## Architecture

### Components

```
lib/ebay/
├── client.ts           # Main eBay API client
├── types.ts            # TypeScript type definitions
├── config.ts           # Configuration management
├── cache.ts            # Redis caching layer
├── rate-limiter.ts     # Bottleneck rate limiter
├── normalizer.ts       # Response normalization
├── index.ts            # Public API exports
└── __tests__/          # Test files
```

### Data Flow

```
User Request
    ↓
EbayClient
    ↓
Check Cache (Redis) ──→ Cache Hit → Return Data
    ↓ Cache Miss
Rate Limiter (Bottleneck)
    ↓
HTTP Request (Axios)
    ↓
eBay API
    ↓
Response Normalizer
    ↓
Cache Result (Redis)
    ↓
Return Data
```

## Performance Considerations

### Cache Hit Rate

With a 24-hour TTL, expect high cache hit rates for popular searches:
- First request: ~5s (API call + normalization)
- Cached requests: ~50ms (Redis lookup)

### Rate Limiting Impact

- Sandbox: Can handle ~5,000 requests/day
- Production: Can handle ~5M requests/day
- Requests are queued when limit is reached (not rejected)

### Memory Usage

Redis memory usage depends on cache size:
- Average item: ~1KB
- 1,000 cached searches: ~1MB
- 10,000 cached searches: ~10MB

## Troubleshooting

### "EBAY_APP_ID environment variable is required"

Make sure your `.env` file exists and contains all required credentials.

### "Redis connection error"

Ensure Redis is running:
```bash
# Start Redis locally
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis
```

### "Rate limit exceeded"

You've hit the daily API call limit. Either:
1. Wait for the limit to reset (24 hours)
2. Upgrade to production environment
3. Use cached data when possible

### Tests timing out

Some tests involve retry logic with delays. This is expected behavior. Tests have appropriate timeouts configured.

## Production Deployment Checklist

- [ ] Set `EBAY_ENVIRONMENT=production`
- [ ] Use production eBay API credentials
- [ ] Configure production Redis instance
- [ ] Set up Redis persistence
- [ ] Configure Redis memory limits
- [ ] Set up monitoring for rate limits
- [ ] Implement cache warming for popular searches
- [ ] Set up error alerting
- [ ] Configure logging levels
- [ ] Test failover scenarios

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review eBay API documentation: https://developer.ebay.com
3. Check Redis documentation: https://redis.io/docs

## Contributing

This module is part of the CardTrail PTCG Price Tracker project. For contributions, please follow the project's contribution guidelines.
