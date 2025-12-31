# Backend Restart Instructions for Railway

## Issue
The GraphQL schema is not showing marketplace queries (`sellers`, `featuredProducts`, `featuredCollections`). This means the backend needs to be restarted or redeployed to pick up the schema changes.

## Solution

### Option 1: Restart the Backend Service (Quick Fix)
1. Go to Railway dashboard: https://railway.app
2. Select your backend service (`hos-saleor-production` or similar)
3. Click on the service
4. Go to the "Settings" tab
5. Click "Restart" button
6. Wait for the service to restart (usually 1-2 minutes)

### Option 2: Redeploy the Backend (Recommended)
1. Go to Railway dashboard
2. Select your backend service
3. Go to the "Deployments" tab
4. Click "Redeploy" on the latest deployment
5. Wait for deployment to complete

### Option 3: Force a New Deployment
If the code is already pushed to GitHub:
1. Railway should auto-deploy on push
2. If not, trigger a manual deployment:
   - Go to the service settings
   - Click "Generate Deploy" or "Redeploy"

## Verify the Fix
After restarting/redeploying, test the GraphQL endpoint:

```bash
curl -X POST https://hos-saleor-production.up.railway.app/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __type(name: \"Query\") { fields(includeDeprecated: true) { name } } }"}' \
  | python3 -m json.tool | grep -i "seller\|featured"
```

You should see fields like:
- `sellers`
- `seller`
- `featuredProducts`
- `featuredCollections`

## Why This Happens
GraphQL schemas are built at application startup. When new queries are added to the code, the backend service must be restarted to rebuild the schema and make the new queries available.

