# Fix Root Directory Error

## Error Message
```
Build Failed: fsutil.NewFS(.../hos-storefront): no such file or directory
```

## Problem
Railway is looking for `hos-storefront` directory in the repository, but it doesn't exist in the git repository (it's only local, not committed).

## Solution Options

### Option 1: Commit and Push hos-storefront to GitHub (Recommended)

1. **Commit the frontend code:**
   ```bash
   cd /Users/apple/HOS-Saleor
   git add hos-storefront/
   git commit -m "Add Next.js frontend"
   git push origin main
   ```

2. **Then in Railway:**
   - Root Directory: `hos-storefront`
   - Railway will find it after you push

### Option 2: Change Root Directory to Repository Root

If `hos-storefront` is not in the repository, you can:

1. **In Railway Dashboard:**
   - Go to: HOS-Storefront → Settings
   - Change **Root Directory** from `hos-storefront` to `/` (root)
   - This assumes Next.js files are in the repository root

2. **Or move files to root:**
   - Move Next.js files from `hos-storefront/` to repository root
   - Commit and push

### Option 3: Create hos-storefront in Repository

If you want to keep the structure:

1. **Commit the folder:**
   ```bash
   cd /Users/apple/HOS-Saleor
   git add hos-storefront/
   git commit -m "Add Next.js frontend application"
   git push origin main
   ```

2. **Verify it's in GitHub:**
   - Go to: https://github.com/Sabuanchuparayil/HOS-Saleor
   - Check if `hos-storefront/` folder exists

3. **In Railway:**
   - Root Directory: `hos-storefront`
   - Railway will find it after push

## Quick Fix Steps

### Step 1: Check if hos-storefront is in Git
```bash
cd /Users/apple/HOS-Saleor
git ls-files | grep hos-storefront | head -5
```

If no output, the folder is not committed.

### Step 2: Commit and Push
```bash
cd /Users/apple/HOS-Saleor
git add hos-storefront/
git status  # Review what will be committed
git commit -m "Add Next.js frontend for Railway deployment"
git push origin main
```

### Step 3: Verify in Railway
- Wait 1-2 minutes for GitHub to sync
- In Railway → HOS-Storefront → Settings
- Verify Root Directory is: `hos-storefront`
- Railway should now find the directory

## Alternative: Deploy from Root

If you don't want to commit `hos-storefront`:

1. **In Railway Dashboard:**
   - Settings → Root Directory
   - Change to: `/` (root)
   - But you'll need to move Next.js files to root or adjust structure

## Recommended Action

**Commit and push the `hos-storefront` folder to GitHub**, then Railway will be able to find it.

