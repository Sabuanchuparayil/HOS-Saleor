# GitHub Repository Connection Guide

## Repository Information

Based on your project structure, you need to connect one of these repositories:

### Option 1: Main Repository (Recommended)
If your `hos-storefront` folder is part of the main HOS-Saleor repository:

**Repository Name:** `HOS-Saleor` (or your actual GitHub repo name)

**Root Directory:** `hos-storefront`

This means:
- Railway connects to your main repository
- Sets root directory to `hos-storefront/` subfolder
- Deploys only the Next.js frontend

### Option 2: Separate Frontend Repository
If `hos-storefront` is in a separate GitHub repository:

**Repository Name:** `hos-storefront` (or your frontend repo name)

**Root Directory:** `/`

## How to Find Your Repository Name

1. **Check your GitHub:**
   - Go to: https://github.com
   - Look for your repository
   - Repository name is shown at the top

2. **Or check locally:**
   ```bash
   cd /Users/apple/HOS-Saleor
   git remote -v
   ```
   This shows your GitHub repository URL

## Connection Steps in Railway

1. **Go to Railway Dashboard:**
   - https://railway.app/dashboard
   - Navigate to: Hos_Saleor → HOS-Storefront → Settings

2. **Connect Repository:**
   - Click **"Connect Repo"** button
   - Authorize Railway (if first time)
   - **Search for your repository:**
     - Type: `HOS-Saleor` or your repo name
     - Select the correct repository

3. **Configure:**
   - **Branch:** `main` (or `master`)
   - **Root Directory:** 
     - If frontend is in `hos-storefront/` folder: Set to `hos-storefront`
     - If frontend is in root: Set to `/`

4. **Deploy:**
   - Railway will automatically start deployment
   - Or click "Deploy" in Deployments tab

## Common Repository Names

Based on your project, it's likely one of these:
- `HOS-Saleor`
- `hos-saleor`
- `HOS-Saleor-Marketplace`
- Or your custom repository name

## Verify Repository

To confirm your repository name, run:
```bash
cd /Users/apple/HOS-Saleor
git remote get-url origin
```

This will show the full GitHub URL, from which you can extract the repository name.

