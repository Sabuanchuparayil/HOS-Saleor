# Steps to Create HOS-Storefront Service

## Step 1: Railway Dashboard (Opened)

The Railway dashboard should now be open in your browser.

## Step 2: Create New Service

In the Railway dashboard:

1. **Navigate to your project:** "Hos_Saleor"
2. **Click the "+ New" button** (usually in the top right or in the services list)
3. **Select "Empty Service"** or **"GitHub Repo"**
   - If using GitHub: Connect your repository
   - If Empty Service: We'll deploy from local files
4. **Name the service:** `HOS-Storefront`
5. **Click "Create" or "Deploy"**

## Step 3: After Service Creation

Once the service is created in the dashboard, come back here and we'll:

1. Link to the new service
2. Set environment variables (if not auto-set)
3. Deploy the frontend

## Quick Commands (Run after creating service in dashboard)

```bash
cd hos-storefront

# Link to the new service
railway service link HOS-Storefront

# Verify environment variables
railway variables

# Deploy
railway up
```

## What to Look For in Dashboard

- Service name: "HOS-Storefront"
- Project: "Hos_Saleor"
- Environment: "production"

Once you see the service created, let me know and we'll proceed with linking and deployment!

