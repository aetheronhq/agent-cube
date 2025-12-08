/**
 * Example Usage of eBay API Client
 * 
 * This file demonstrates how to use the eBay API client.
 * 
 * To run this example:
 * 1. Set up your .env file with eBay credentials
 * 2. Ensure Redis is running
 * 3. Run: npx ts-node lib/ebay/example.ts
 */

import { EbayClient } from './client';

async function main(): Promise<void> {
  console.log('=== eBay API Client Example ===\n');

  // Create client instance
  const client = new EbayClient();

  try {
    // Check cache connection
    console.log('Cache connected:', client.isCacheConnected());

    // Example 1: Search for completed Pokemon card sales
    console.log('\n--- Example 1: Completed Pokemon Card Sales ---');
    const completedResults = await client.findCompletedItems({
      keywords: 'Pokemon Charizard',
      soldItemsOnly: true,
      minPrice: 10,
      maxPrice: 500
    });

    console.log(`Found ${completedResults.totalResults} completed items`);
    console.log(`Showing first ${Math.min(5, completedResults.items.length)} items:\n`);

    completedResults.items.slice(0, 5).forEach((item, index) => {
      console.log(`${index + 1}. ${item.title}`);
      console.log(`   Price: $${item.price} ${item.currency}`);
      console.log(`   Condition: ${item.condition}`);
      console.log(`   Listing Type: ${item.listingType}`);
      console.log(`   Sold: ${item.isSold ? 'Yes' : 'No'}`);
      console.log(`   End Date: ${item.endDate.toISOString()}`);
      if (item.location) {
        console.log(`   Location: ${item.location}`);
      }
      console.log();
    });

    // Example 2: Search for active listings
    console.log('\n--- Example 2: Active Pokemon Card Listings ---');
    const activeResults = await client.findItemsAdvanced({
      keywords: 'Pokemon Pikachu',
      condition: 'New',
      minPrice: 5,
      maxPrice: 100
    });

    console.log(`Found ${activeResults.totalResults} active items`);
    console.log(`Showing first ${Math.min(3, activeResults.items.length)} items:\n`);

    activeResults.items.slice(0, 3).forEach((item, index) => {
      console.log(`${index + 1}. ${item.title}`);
      console.log(`   Current Price: $${item.price} ${item.currency}`);
      console.log(`   Condition: ${item.condition}`);
      console.log();
    });

    // Example 3: Cache statistics
    console.log('\n--- Example 3: Cache Statistics ---');
    const stats = await client.getCacheStats();
    console.log(`Total cached keys: ${stats.totalKeys}`);
    console.log(`Memory usage: ${stats.memoryUsage}`);

    // Example 4: Demonstrate cache hit
    console.log('\n--- Example 4: Cache Hit Demonstration ---');
    console.log('Making same request again (should use cache)...');
    const startTime = Date.now();
    await client.findCompletedItems({
      keywords: 'Pokemon Charizard',
      soldItemsOnly: true,
      minPrice: 10,
      maxPrice: 500
    });
    const endTime = Date.now();
    console.log(`Request completed in ${endTime - startTime}ms (cached)`);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Always close connections
    console.log('\n--- Closing Connections ---');
    await client.close();
    console.log('Done!');
  }
}

// Run the example
if (require.main === module) {
  main().catch(console.error);
}

export { main };
