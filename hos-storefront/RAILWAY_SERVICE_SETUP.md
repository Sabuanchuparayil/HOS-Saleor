# Railway Service Setup for Frontend

## Current Status

✅ **Environment Variables Set:**
- `NEXT_PUBLIC_SALEOR_API_URL` = https://hos-saleor-production.up.railway.app/graphql/
- `NEXT_PUBLIC_SITE_URL` = https://hos-marketplaceweb-production.up.railway.app
- `NODE_ENV` = production

⚠️ **Current Service:** HOS-Saleor (Backend service)

## Issue

Railway CLI v4 doesn't support `railway service create --name`. Services must be created through the Railway dashboard.

## Solution: Create Service via Railway Dashboard

### Step 1: Open Railway Dashboard
```bash
railway open
```

### Step 2: Create New Service
1. In the Railway dashboard, go to your project "Hos_Saleor"
2. Click **"+ New"** button
3. Select **"Empty Service"** or **"GitHub Repo"**
4. Name it: **"HOS-Storefront"**

### Step 3: Link to the New Service
After creating the service in the dashboard:

```bash
cd hos-storefront
railway service link HOS-Storefront
```

### Step 4: Set Environment Variables
```bash
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"
```

### Step 5: Deploy
```bash
railway up
```

## Alternative: Deploy to Current Service

If you want to deploy the frontend to the existing HOS-Saleor service (not recommended, but possible):

```bash
cd hos-storefront
railway up
```

**Note:** This will deploy Next.js to the same service as Django. You'll need to configure routing or use different ports.

## Check Deployment Status

```bash
# View logs
railway logs

# Get URL
railway domain

# Check status
railway status
```

## Recommended Approach

1. **Create service via dashboard:** `railway open` → Create new service "HOS-Storefront"
2. **Link service:** `railway service link HOS-Storefront`
3. **Set variables:** (Already done, but verify)
4. **Deploy:** `railway up`

This keeps your frontend and backend as separate services, which is the best practice.

