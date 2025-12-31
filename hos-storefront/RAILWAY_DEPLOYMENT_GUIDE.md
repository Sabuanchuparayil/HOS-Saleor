# Railway Deployment Guide for Next.js Frontend

## Current Status
✅ Environment variables are set:
- `NEXT_PUBLIC_SALEOR_API_URL` = https://hos-saleor-production.up.railway.app/graphql/
- `NEXT_PUBLIC_SITE_URL` = https://hos-marketplaceweb-production.up.railway.app
- `NODE_ENV` = production

## Deployment Steps

### Option 1: Create New Service for Frontend (Recommended)

Since you already have a backend service (HOS-Saleor), create a separate service for the frontend:

```bash
cd hos-storefront

# Create a new service for the frontend
railway service create --name "HOS-Storefront"

# Link to the new service
railway service link HOS-Storefront

# Set environment variables for the frontend service
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

# Deploy
railway up
```

### Option 2: Deploy to Existing Service (If you want to use the same service)

If you want to deploy the frontend to the existing HOS-Saleor service:

```bash
cd hos-storefront

# Make sure you're linked to the right service
railway service link HOS-Saleor

# Set environment variables
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

# Deploy
railway up
```

## Verify Deployment

After deployment:

1. **Check deployment status:**
   ```bash
   railway logs
   ```

2. **Get your app URL:**
   ```bash
   railway domain
   ```

3. **Open in browser:**
   ```bash
   railway open
   ```

## Troubleshooting

### Build Fails
- Check Node.js version (should be 20.x)
- Verify `package.json` has correct build scripts
- Check logs: `railway logs`

### Environment Variables Not Working
- Verify variables are set: `railway variables`
- Make sure variables start with `NEXT_PUBLIC_` for client-side access
- Check Railway dashboard for variable visibility

### Service Not Found
- List services: Check Railway dashboard
- Create new service: `railway service create --name "YourServiceName"`
- Link service: `railway service link YourServiceName`

## Next Steps After Deployment

1. ✅ Verify homepage loads
2. ✅ Test product listing
3. ✅ Check GraphQL queries work
4. ✅ Test cart and checkout
5. ✅ Verify SEO (sitemap, robots.txt)
6. ✅ Test mobile responsiveness

