# Fix Root Directory - Remove Leading Slash

## Problem
Root Directory is set to `/hos-storefront` (with leading slash) which Railway interprets as an absolute path, causing build failures.

## Solution
Change Root Directory from `/hos-storefront` to `hos-storefront` (without leading slash).

## Steps to Fix

### In Railway Dashboard:

1. **Go to:** HOS-Storefront → Settings tab
2. **Find:** "Root Directory" field
3. **Change from:** `/hos-storefront`
4. **Change to:** `hos-storefront` (remove the leading `/`)
5. **Click:** Save or the field should auto-save
6. **Wait:** Railway will automatically trigger a new deployment

## Why This Matters

- `/hos-storefront` = Absolute path from filesystem root (doesn't exist)
- `hos-storefront` = Relative path from repository root (correct)

## After Fixing

Railway will:
1. ✅ Find the `hos-storefront` folder in your repository
2. ✅ Start a new build automatically
3. ✅ Deploy successfully

## Verify

After changing, check:
- Deployments tab should show a new deployment starting
- Build logs should show "found 'railway.toml' at 'railway.toml'"
- No more "no such file or directory" errors

