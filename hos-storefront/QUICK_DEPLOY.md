# Quick Deploy to Railway

## Current Status
✅ Environment variables are already set in Railway
✅ Railway CLI is installed and logged in
✅ Project is linked to "Hos_Saleor" project

## Quick Deploy Command

Since you're currently linked to the backend service (HOS-Saleor), you have two options:

### Option 1: Deploy Frontend to New Service (Recommended)

```bash
cd hos-storefront

# Create and link to new frontend service
railway service create --name "HOS-Storefront"
railway service link HOS-Storefront

# Set variables (if not already set)
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

# Deploy
railway up
```

### Option 2: Deploy to Current Service

If you want to deploy the frontend to the existing service:

```bash
cd hos-storefront
railway up
```

**Note:** This will deploy the Next.js app to the same service as your Django backend, which may not be ideal. It's better to create a separate service.

## Check Deployment

```bash
# View logs
railway logs

# Get URL
railway domain

# Open dashboard
railway open
```

## Environment Variables Already Set

The following variables are already configured:
- ✅ `NEXT_PUBLIC_SALEOR_API_URL`
- ✅ `NEXT_PUBLIC_SITE_URL`
- ✅ `NODE_ENV`

You can verify with:
```bash
railway variables | grep NEXT_PUBLIC
```

