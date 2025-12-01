# Performance Optimizations

This document describes the performance optimizations implemented to improve app speed and responsiveness.

## Optimizations Implemented

### 1. **In-Memory Caching**
- Added `CacheService` for caching API responses
- Reduces redundant network requests
- Cache TTL (Time To Live):
  - Inventory: 2 minutes
  - Users: 5 minutes
  - Cart: 10 seconds (short because it changes frequently)

### 2. **Lazy Screen Loading**
- Screens are now created only when needed (when tab is selected)
- Previously, all screens were instantiated at app start, causing unnecessary API calls
- Reduces initial load time and memory usage

### 3. **Request Timeout**
- Added 10-second timeout to all API requests
- Prevents hanging requests that slow down the app
- Faster failure detection

### 4. **Optimized Retry Logic**
- Reduced max retries from 2 to 1 (faster failure)
- Reduced retry delay from 1 second to 500ms
- Only retries on network errors, not client errors (4xx)

### 5. **Smart Cache Invalidation**
- Cache is automatically invalidated when data is modified
- Ensures users always see fresh data after changes
- Prevents stale data issues

### 6. **Conditional Caching**
- Search queries are not cached (always fresh results)
- Regular list views are cached for faster loading
- Cart is cached for only 10 seconds due to frequent changes

## Performance Impact

### Before Optimizations:
- Every screen switch = new API call
- All screens loaded at startup
- No caching = repeated network requests
- Slow retry logic = long wait times

### After Optimizations:
- ✅ Cached responses = instant loading (when cache valid)
- ✅ Lazy loading = faster app startup
- ✅ Timeout = faster error detection
- ✅ Optimized retries = quicker failures
- ✅ Smart invalidation = fresh data when needed

## Expected Improvements

- **Initial Load**: 30-50% faster (lazy screen loading)
- **Subsequent Loads**: 70-90% faster (caching)
- **Error Handling**: 50% faster (reduced retries, timeouts)
- **Memory Usage**: 20-30% lower (lazy loading)

## Cache Management

### Manual Cache Control

You can manually control caching in API calls:

```dart
// Force fresh data (bypass cache)
final products = await apiService.getInventory(useCache: false);

// Use cache (default)
final products = await apiService.getInventory(useCache: true);
```

### Clear Cache Programmatically

```dart
// Clear all cache
CacheService().clear();

// Clear specific cache
ApiService.invalidateInventoryCache();
ApiService.invalidateCartCache();
ApiService.invalidateUsersCache();
```

## Monitoring Performance

To check if caching is working:
1. Load a screen (e.g., Inventory)
2. Switch to another screen
3. Switch back - should load instantly from cache
4. Wait for cache TTL to expire
5. Switch back - will fetch fresh data

## Future Optimizations (Optional)

If you need even better performance, consider:
1. **Persistent Cache**: Use `shared_preferences` to cache across app restarts
2. **Image Caching**: Cache product images if you add them
3. **Pagination**: Load data in smaller chunks
4. **Background Sync**: Pre-fetch data in background
5. **Compression**: Enable gzip compression on API responses

## Troubleshooting

### App Still Feels Slow?

1. **Check Network**: Slow network = slow API calls
   - Test API directly: `http://YOUR_IP:8000`
   - Check ping time to server

2. **Disable Cache Temporarily**: 
   ```dart
   // In api_service.dart, set useCache: false
   ```

3. **Check Cache Hit Rate**: 
   - Add logging to see cache hits/misses
   - Verify cache is working

4. **Reduce Cache TTL**: 
   - If data changes frequently, reduce cache duration
   - Edit `cacheTtl` in API service methods

5. **Check for Memory Issues**:
   - Large datasets might need pagination
   - Consider limiting page size

