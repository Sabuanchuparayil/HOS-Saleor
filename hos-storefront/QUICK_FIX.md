# Quick Fix: Connect GitHub Repo

## The Problem
- Project is 513MB (too large for fast CLI upload)
- Indexing is slow because Railway uploads all files
- Service is offline waiting for deployment

## The Solution: Connect GitHub (2 minutes)

### In Railway Dashboard:

1. **Go to:** https://railway.app/dashboard
2. **Navigate to:** Hos_Saleor → HOS-Storefront → Settings
3. **Click:** "Connect Repo" button
4. **Select:** Your GitHub repository
5. **Select branch:** `main`
6. **Set Root Directory:** `hos-storefront` (if Next.js is in that folder)
7. **Done!** Railway will auto-deploy (much faster!)

## Why This Works

- ✅ Railway uses git (fast)
- ✅ Only changed files are synced
- ✅ No large file uploads
- ✅ Auto-deploys on every push
- ✅ Builds in 2-3 minutes instead of 15-20 minutes

## Environment Variables (Already Set)

These are already configured:
- `NEXT_PUBLIC_SALEOR_API_URL`
- `NEXT_PUBLIC_SITE_URL`
- `NODE_ENV`

## After Connecting Repo

Railway will:
1. Detect Next.js automatically
2. Install dependencies (`npm install`)
3. Build the app (`npm run build`)
4. Start the server (`npm start`)
5. Your app goes live!

**URL:** https://hos-storefront-production.up.railway.app

