# Railway Deployment Fixes

## Issues Found

1. ❌ **Root Directory has leading slash:** `/hos-storefront` (incorrect)
2. ❌ **Node.js version too old:** 18.20.5 (Next.js requires >=20.9.0)

## Fixes Applied

### ✅ Fix 1: Node.js Version
- Created `.nvmrc` file specifying Node.js 20.18.0
- Created `nixpacks.toml` to ensure Railway uses Node.js 20
- Updated `railway.toml` with Nixpacks config
- **Committed and pushed to GitHub**

### ⚠️ Fix 2: Root Directory (Manual Step Required)

**You need to fix this in Railway Dashboard:**

1. Go to: **HOS-Storefront → Settings tab**
2. Find: **"Root Directory"** field
3. **Change from:** `/hos-storefront` (with leading slash)
4. **Change to:** `hos-storefront` (without leading slash)
5. The field should auto-save
6. Railway will automatically trigger a new deployment

## Why These Fixes Matter

### Root Directory
- `/hos-storefront` = Absolute path (doesn't exist in Railway's filesystem)
- `hos-storefront` = Relative path from repo root (correct)

### Node.js Version
- Next.js 16 requires Node.js >=20.9.0
- Railway was using Node.js 18.20.5 by default
- Now explicitly configured to use Node.js 20

## After Both Fixes

Railway will:
1. ✅ Find the `hos-storefront` folder (correct root directory)
2. ✅ Use Node.js 20 (compatible with Next.js 16)
3. ✅ Build successfully
4. ✅ Deploy the frontend

## Verify

After fixing Root Directory in dashboard:
- Check Deployments tab for new build
- Build logs should show Node.js 20
- Build should complete successfully
- Service should go online

## Quick Summary

**Action Required:**
1. In Railway Dashboard → HOS-Storefront → Settings
2. Change Root Directory: `/hos-storefront` → `hos-storefront`
3. Wait for automatic deployment

**Already Fixed:**
- ✅ Node.js version (committed to GitHub)
- ✅ Repository connection
- ✅ Environment variables

