# Complete Deployment Instructions

## Why Indexing is Slow

Your project is **513MB** with **29,823 files**, including:
- `node_modules/` folder: **496MB** (should NOT be uploaded)
- Railway is trying to upload all files via CLI

**Solution:** Connect GitHub repo (faster) or use `.railwayignore` (I've created this file)

## ✅ Option 1: Connect GitHub Repo (FASTEST - Recommended)

### Steps in Railway Dashboard:

1. **Go to Railway Dashboard:**
   - URL: https://railway.app/dashboard
   - Navigate to: **Hos_Saleor** project → **HOS-Storefront** service

2. **Connect GitHub Repository:**
   - Click **"Settings"** tab
   - Scroll to **"Connect Source"** section
   - Click **"Connect Repo"** button (GitHub icon)
   - Authorize Railway to access your GitHub
   - Select repository: Your HOS-Saleor repository
   - Select branch: `main` (or your default branch)
   - Click **"Connect"**

3. **Set Root Directory:**
   - In Settings → **"Root Directory"**
   - If Next.js app is in `hos-storefront/` folder: Set to `hos-storefront`
   - If Next.js app is in root: Leave as `/`

4. **Verify Build Settings:**
   - Railway auto-detects Next.js
   - Build Command: `npm run build` (should be auto-set)
   - Start Command: `npm start` (should be auto-set)

5. **Verify Environment Variables:**
   - Go to **"Variables"** tab
   - Ensure these are set:
     ```
     NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/
     NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app
     NODE_ENV=production
     ```

6. **Deploy:**
   - Railway will automatically deploy when repo is connected
   - Or go to **"Deployments"** tab and click **"Deploy"**

**This method is MUCH faster** because Railway uses git instead of uploading all files!

## ✅ Option 2: Complete CLI Deployment (Current Method)

I've created `.railwayignore` to exclude large folders. The deployment should proceed faster now.

### Monitor Deployment:

```bash
cd hos-storefront

# View live logs
railway logs

# Check deployment status
railway deployment list

# If stuck, cancel and retry
railway down
railway up
```

### What `.railwayignore` Excludes:
- `node_modules/` (496MB - will be installed during build)
- `.next/` (build output)
- `.git/` (git files)
- Documentation files
- Other unnecessary files

This reduces upload from 513MB to ~20MB, making indexing much faster.

## 📋 Manual Configuration (If Needed)

### In Railway Dashboard → HOS-Storefront → Settings:

1. **Build Settings:**
   - Builder: `NIXPACKS` (auto-detected)
   - Build Command: `npm run build`
   - Start Command: `npm start`

2. **Environment Variables (Variables tab):**
   ```
   NEXT_PUBLIC_SALEOR_API_URL = https://hos-saleor-production.up.railway.app/graphql/
   NEXT_PUBLIC_SITE_URL = https://hos-marketplaceweb-production.up.railway.app
   NODE_ENV = production
   ```

3. **Root Directory:**
   - If Next.js is in `hos-storefront/`: Set to `hos-storefront`
   - If in root: Set to `/`

4. **Networking:**
   - Domain should be: `hos-storefront-production.up.railway.app`
   - (Already configured)

## 🚀 Recommended: Connect GitHub

**Why GitHub is better:**
- ✅ Much faster (uses git, not file upload)
- ✅ Auto-deploys on push
- ✅ Better version control
- ✅ No indexing delays

**Steps:**
1. Make sure your code is pushed to GitHub
2. In Railway → HOS-Storefront → Settings
3. Click "Connect Repo"
4. Select your repository
5. Railway auto-deploys!

## 📊 Check Status

```bash
cd hos-storefront

# View logs
railway logs

# Check deployments
railway deployment list

# Get URL
railway domain
```

## ⏱️ Expected Timeline

- **With GitHub:** 2-3 minutes (build only)
- **With CLI (after .railwayignore):** 5-8 minutes (upload + build)
- **With CLI (before .railwayignore):** 15-20 minutes (uploading 513MB)

## ✅ Next Steps

1. **Best option:** Connect GitHub repo in Railway dashboard
2. **Alternative:** Wait for current CLI deployment (with .railwayignore it should be faster)
3. **Monitor:** Check `railway logs` for progress

Your frontend will be live at: **https://hos-storefront-production.up.railway.app**

