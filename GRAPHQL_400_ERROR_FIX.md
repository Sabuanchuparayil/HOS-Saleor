# GraphQL 400 Error Fix - Root Cause Identified

## Error Messages from Backend

When querying the backend directly, we get these errors:

1. **`sellers` query:**
   ```json
   {
     "errors": [{
       "message": "Cannot query field \"sellers\" on type \"Query\". Did you mean \"sales\"?",
       "locations": [{"line": 1, "column": 3}]
     }]
   }
   ```

2. **`featuredProducts` query:**
   ```json
   {
     "errors": [{
       "message": "Cannot query field \"featuredProducts\" on type \"Query\".",
       "locations": [{"line": 1, "column": 3}]
     }]
   }
   ```

## Root Cause

**CONFIRMED:** The backend GraphQL schema does not include the marketplace queries (`sellers`, `featuredCollections`, `featuredProducts`) because **the backend service has not been restarted** to rebuild the schema.

### Evidence

1. ✅ Code is correct: `HomepageQueries` and `SellerQueries` are registered in `saleor/graphql/api.py` (lines 69, 73)
2. ✅ Resolvers exist: `resolve_featured_collections`, `resolve_featured_products`, `resolve_sellers` are implemented
3. ❌ Schema introspection shows these fields are missing from the Query type
4. ❌ Direct queries to the backend return "Cannot query field" errors

## Solution

**Restart the backend service on Railway:**

1. Go to Railway dashboard: https://railway.app
2. Select your **backend service** (`hos-saleor-production`)
3. Go to **Settings** tab
4. Click **Restart** button
5. Wait 1-2 minutes for the service to restart

**OR** redeploy:

1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment

## Verification

After restarting, verify the schema includes the marketplace queries:

```bash
curl -X POST https://hos-saleor-production.up.railway.app/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __type(name: \"Query\") { fields { name } } }"}' \
  | python3 -m json.tool | grep -E "sellers|featured"
```

You should see:
- `sellers`
- `featuredCollections` 
- `featuredProducts`

## Why This Happens

GraphQL schemas in Saleor are built at **application startup**. When new queries are added to the code:

1. The code defines the queries (✅ Done)
2. The queries are registered in the Query class (✅ Done)
3. **The application must be restarted** to rebuild the schema (❌ Not done yet)

The running backend service is using an old schema that was built before the marketplace queries were added.

## Expected Behavior After Fix

Once the backend is restarted:
- ✅ `sellers` query will work
- ✅ `featuredCollections` query will work
- ✅ `featuredProducts` query will work
- ✅ All 400 errors will be resolved
- ✅ Frontend will be able to fetch data successfully

