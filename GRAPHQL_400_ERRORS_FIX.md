# GraphQL 400 Bad Request Errors - Fix Summary

## Issues Fixed

### 1. ✅ Missing `pageInfo` in Connection Queries
**Problem:** `featuredProducts` and `featuredCollections` queries were missing the required `pageInfo` field for ConnectionField types.

**Fix Applied:**
- Added `pageInfo` field to `GET_FEATURED_PRODUCTS` query
- Added `pageInfo` field to `GET_FEATURED_COLLECTIONS` query

**Files Changed:**
- `hos-storefront/lib/graphql/queries.ts`

### 2. ✅ Apollo Client TypeScript Error
**Problem:** `fetchPolicy: "cache-and-network"` is not a valid type in Apollo Client 4.0.11's `defaultOptions`.

**Fix Applied:**
- Removed `fetchPolicy` from `defaultOptions` in Apollo Client configuration
- Individual queries can still set `fetchPolicy` in their `useQuery` calls

**Files Changed:**
- `hos-storefront/lib/apollo-client.ts`

### 3. ✅ Exception Handling Bug
**Problem:** `ImportError` was catching errors from function calls, not just imports.

**Fix Applied:**
- Separated import statements from function calls using try-except-else pattern
- Now `ImportError` only catches import failures, function errors are properly logged

**Files Changed:**
- `saleor/order/actions.py`

## Remaining Issues to Investigate

### Possible Causes of Continued 400 Errors:

1. **CORS Configuration**
   - ✅ `ALLOWED_GRAPHQL_ORIGINS` is set in Railway
   - ⚠️ Verify the exact frontend URL matches (check for trailing slashes, http vs https)

2. **GraphQL Query Validation**
   - The queries might be valid but rejected for other reasons
   - Check backend logs for specific GraphQL validation errors
   - Verify all required fields are present

3. **Channel Parameter**
   - Some queries require a `channel` parameter
   - Verify if `channel` should be required or have a default value

4. **Schema Registration**
   - Verify `HomepageQueries` is properly registered in the main GraphQL schema
   - Check if `featuredProducts` and `featuredCollections` are accessible

## Debugging Steps

### 1. Check Backend Logs
```bash
railway logs --service HOS-Saleor
```

Look for:
- GraphQL validation errors
- CORS errors
- Missing field errors

### 2. Test Queries Directly
Use GraphQL Playground or Postman to test queries directly:

```graphql
query TestFeaturedProducts {
  featuredProducts(first: 8) {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

### 3. Check Network Tab
In browser DevTools:
- Check the actual request payload
- Check the response body for error details
- Verify CORS headers are present

### 4. Verify Environment Variables
```bash
railway variables
```

Ensure:
- `ALLOWED_GRAPHQL_ORIGINS` includes the exact frontend URL
- No trailing slashes or protocol mismatches

## Next Steps

1. **Check Railway Backend Logs** for specific error messages
2. **Test queries in GraphQL Playground** to isolate the issue
3. **Verify CORS headers** in the response
4. **Check if queries work without optional parameters** (like `channel`)

## Files Modified

- ✅ `hos-storefront/lib/graphql/queries.ts` - Added pageInfo
- ✅ `hos-storefront/lib/apollo-client.ts` - Fixed fetchPolicy
- ✅ `saleor/order/actions.py` - Fixed exception handling
- ✅ `hos-storefront/components/product/FeaturedProducts.tsx` - Fixed data path
- ✅ `hos-storefront/components/collection/FeaturedCollections.tsx` - Fixed data path

## Status

- ✅ TypeScript compilation errors: Fixed
- ✅ Missing pageInfo: Fixed
- ✅ Exception handling: Fixed
- ⚠️ GraphQL 400 errors: Under investigation

The frontend should redeploy automatically with these fixes. If 400 errors persist, check the backend logs for specific GraphQL validation errors.

