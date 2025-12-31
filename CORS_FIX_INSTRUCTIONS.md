# CORS Fix Instructions for Railway

## Issue
The frontend at `https://hos-storefront-production.up.railway.app` cannot make requests to the backend at `https://hos-saleor-production.up.railway.app` due to CORS (Cross-Origin Resource Sharing) policy blocking.

## Error Message
```
Access to fetch at 'https://hos-saleor-production.up.railway.app/graphql/' 
from origin 'https://hos-storefront-production.up.railway.app' has been blocked 
by CORS policy: Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution

### Step 1: Set the CORS Environment Variable on Railway Backend

1. Go to Railway dashboard: https://railway.app
2. Select your **backend service** (`hos-saleor-production` or similar)
3. Go to the **Variables** tab
4. Add or update the following environment variable:

   **Variable Name:** `ALLOWED_GRAPHQL_ORIGINS`
   
   **Variable Value:** 
   ```
   https://hos-storefront-production.up.railway.app
   ```
   
   **OR** to allow all origins (less secure, but useful for development):
   ```
   *
   ```

   **OR** to allow multiple origins (comma-separated):
   ```
   https://hos-storefront-production.up.railway.app,https://localhost:3000,http://localhost:3000
   ```

### Step 2: Restart the Backend Service

After setting the environment variable:

1. Go to the **Settings** tab of your backend service
2. Click **Restart** to apply the changes
3. Wait for the service to restart (usually 1-2 minutes)

### Step 3: Verify the Fix

After restarting, test the CORS configuration:

```bash
curl -X OPTIONS https://hos-saleor-production.up.railway.app/graphql/ \
  -H "Origin: https://hos-storefront-production.up.railway.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

You should see:
- `Access-Control-Allow-Origin: https://hos-storefront-production.up.railway.app`
- Status code: 200

## How CORS Works in Saleor

Saleor uses a custom CORS handler (`saleor/asgi/cors_handler.py`) that:
1. Checks the `Origin` header in incoming requests
2. Matches it against `ALLOWED_GRAPHQL_ORIGINS` using pattern matching
3. Adds appropriate CORS headers if the origin is allowed
4. Handles preflight OPTIONS requests

The configuration is read from the `ALLOWED_GRAPHQL_ORIGINS` environment variable, which defaults to `*` (allow all) if not set.

## Security Note

- Using `*` allows all origins (less secure)
- For production, specify exact origins
- You can use wildcards like `https://*.railway.app` to match all Railway subdomains

## Alternative: Quick Fix via Railway CLI

If you have Railway CLI installed:

```bash
railway variables set ALLOWED_GRAPHQL_ORIGINS="https://hos-storefront-production.up.railway.app" --service <your-backend-service-id>
railway restart --service <your-backend-service-id>
```

