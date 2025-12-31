# Manual Deployment Guide for HOS-Storefront

## Current Situation
- ✅ Service created: HOS-Storefront
- ✅ Environment variables set
- ✅ Domain assigned: https://hos-storefront-production.up.railway.app
- ⚠️ Service is offline (no deployment yet)
- ⚠️ No source connected (no GitHub repo)

## Option 1: Connect GitHub Repo (Recommended - Faster)

### Steps in Railway Dashboard:

1. **Open Railway Dashboard:**
   - Go to: https://railway.app/dashboard
   - Navigate to: Hos_Saleor → HOS-Storefront

2. **Connect Repository:**
   - Click on **"Settings"** tab
   - Find **"Connect Source"** section
   - Click **"Connect Repo"** button
   - Select your GitHub repository
   - Choose the branch (usually `main` or `master`)
   - Railway will auto-detect Next.js and configure build settings

3. **Set Root Directory (if needed):**
   - If your Next.js app is in a subdirectory (like `hos-storefront/`)
   - In Settings → Root Directory, set it to: `hos-storefront`
   - If it's in the root, leave it as `/`

4. **Verify Environment Variables:**
   - Go to **"Variables"** tab
   - Verify these are set:
     - `NEXT_PUBLIC_SALEOR_API_URL` = https://hos-saleor-production.up.railway.app/graphql/
     - `NEXT_PUBLIC_SITE_URL` = https://hos-marketplaceweb-production.up.railway.app
     - `NODE_ENV` = production

5. **Deploy:**
   - Railway will automatically deploy when you connect the repo
   - Or click **"Deploy"** button in the Deployments tab

## Option 2: Deploy via CLI (Current Method)

### If indexing is still in progress:

1. **Wait for indexing to complete** (can take 5-10 minutes for first deployment)

2. **Monitor progress:**
   ```bash
   cd hos-storefront
   railway logs
   ```

3. **Check deployment status:**
   ```bash
   railway deployment list
   ```

### If indexing failed or stuck:

1. **Cancel and retry:**
   ```bash
   cd hos-storefront
   railway down  # Cancel current deployment
   railway up    # Retry deployment
   ```

2. **Check for large files:**
   - Make sure `node_modules/` is in `.gitignore`
   - Railway should install dependencies during build, not upload them

3. **Use .railwayignore:**
   - I've created `.railwayignore` file to exclude unnecessary files
   - This speeds up indexing

## Option 3: Manual Configuration in Dashboard

### If CLI deployment doesn't work:

1. **Set Build Settings:**
   - Go to Settings → Build
   - Build Command: `npm run build`
   - Start Command: `npm start`
   - Root Directory: `/` (or `hos-storefront` if in subdirectory)

2. **Set Environment Variables:**
   - Go to Variables tab
   - Add these variables:
     ```
     NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/
     NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app
     NODE_ENV=production
     ```

3. **Deploy:**
   - Go to Deployments tab
   - Click "Deploy" or "Redeploy"

## Why Indexing is Slow

1. **First-time deployment:** Railway needs to upload all files
2. **Large project:** Many files take time to scan and upload
3. **Network speed:** Uploading to Railway servers
4. **Railway queue:** Other deployments in queue

## Quick Fix: Connect GitHub (Fastest)

**Recommended approach:**
1. Push your code to GitHub (if not already)
2. In Railway dashboard → Connect Repo
3. Railway will auto-deploy (much faster than CLI upload)

## Check Current Status

```bash
cd hos-storefront

# View logs
railway logs

# Check deployments
railway deployment list

# Get URL
railway domain
```

## Expected Build Process

Once indexing completes, you should see:
1. ✅ Installing dependencies (`npm install`)
2. ✅ Building Next.js (`npm run build`)
3. ✅ Generating sitemap (`next-sitemap`)
4. ✅ Starting server (`npm start`)
5. ✅ Service goes online

## Troubleshooting

### If indexing never completes:
- Try connecting GitHub repo instead
- Check Railway dashboard for error messages
- Verify `.railwayignore` is excluding large folders
- Try deploying from a smaller directory

### If build fails:
- Check logs: `railway logs`
- Verify `package.json` has correct build scripts
- Check Node.js version (should be 20.x)
- Verify environment variables are set

