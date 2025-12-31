# Railway Deployment Instructions

## Current Situation

✅ Environment variables are set correctly
⚠️ Currently linked to backend service (HOS-Saleor)
⚠️ Railway CLI v4 doesn't support `service create` command

## Quick Solution

### Option 1: Create Service via Dashboard (Recommended)

1. **Open Railway Dashboard:**
   ```bash
   railway open
   ```

2. **In the Dashboard:**
   - Click **"+ New"** in your project
   - Select **"Empty Service"**
   - Name it: **"HOS-Storefront"**

3. **Link to the new service:**
   ```bash
   railway service link HOS-Storefront
   ```

4. **Verify environment variables:**
   ```bash
   railway variables
   ```
   (They should already be set, but verify)

5. **Deploy:**
   ```bash
   railway up
   ```

### Option 2: Deploy to Current Service

If you want to deploy now without creating a new service:

```bash
cd hos-storefront
railway up
```

**Note:** This deploys Next.js to the Django service. You may need to configure routing.

## Check Deployment

After deployment:

```bash
# View logs
railway logs

# Get your URL
railway domain

# Open dashboard
railway open
```

## Environment Variables (Already Set)

- ✅ `NEXT_PUBLIC_SALEOR_API_URL`
- ✅ `NEXT_PUBLIC_SITE_URL`
- ✅ `NODE_ENV`

Verify with:
```bash
railway variables | grep NEXT_PUBLIC
```

## Next Steps

1. Create service in dashboard OR deploy to current service
2. Wait for deployment to complete
3. Visit the URL from `railway domain`
4. Test the frontend

