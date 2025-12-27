# Manual Deployment Trigger Guide

If Railway isn't automatically detecting changes or starting a deployment, here's how to manually trigger it.

## Option 1: Trigger Redeploy in Railway Dashboard

1. Go to **Railway Dashboard** → **Saleor Service**
2. Click on **"Deployments"** tab
3. Find the latest deployment
4. Click **"Redeploy"** or **"Redeploy Latest"** button
5. This will trigger a new deployment with the latest code

## Option 2: Make a Small Change to Trigger Deployment

If automatic deployments aren't working, make a small change:

1. **Create a trigger file:**
   ```bash
   echo "$(date)" > .railway-trigger
   git add .railway-trigger
   git commit -m "Trigger Railway deployment"
   git push github main
   ```

2. Railway should detect the change and trigger a new deployment

## Option 3: Check Railway Service Settings

1. Go to **Railway Dashboard** → **Saleor Service** → **Settings**
2. Check **"Source"** section
3. Verify:
   - Repository is connected correctly
   - Branch is set to `main` (or your default branch)
   - Auto-deploy is enabled (if available)

## Option 4: Check Railway Project Settings

1. Go to **Railway Dashboard** → **Project Settings**
2. Check **"Git Repository"** section
3. Verify:
   - Repository is connected
   - Service is linked to the repository
   - Auto-deploy is enabled

## Option 5: Force Push (if needed)

If changes aren't being detected:

```bash
# Make sure you're on the right branch
git checkout main

# Verify changes are committed
git log --oneline -3

# Force push (use with caution)
git push github main --force
```

## Option 6: Disconnect and Reconnect Repository

1. Railway Dashboard → Saleor Service → Settings → Source
2. Disconnect the repository
3. Reconnect the repository
4. Select the correct branch
5. This should trigger a new deployment

## Verify Changes Are Pushed

Before trying manual triggers, verify your changes are on GitHub:

1. Go to your GitHub repository: `https://github.com/Sabuanchuparayil/saleor`
2. Check the latest commit
3. Verify `start.sh` has the PORT_VAL fix
4. Verify `railway.toml` and `Dockerfile` are correct

## Check Railway Logs

Even if deployment isn't starting, check:

1. Railway Dashboard → Saleor Service → Deployments
2. Look for any error messages
3. Check if there are any pending or failed deployments
4. Look for webhook/trigger errors

## Common Issues

### Changes Not Detected
- Railway might be watching a different branch
- GitHub webhooks might not be configured
- Repository might not be properly connected

### Deployment Queued but Not Starting
- Check Railway service limits/quota
- Check if there are other deployments in progress
- Verify service isn't paused or disabled

### No Deployment Triggered
- Make sure commits are pushed to the connected branch
- Check Railway project settings for auto-deploy
- Try manual redeploy from dashboard

## Quick Checklist

- [ ] Changes are committed locally
- [ ] Changes are pushed to GitHub (`git push github main`)
- [ ] Repository is connected in Railway dashboard
- [ ] Correct branch is selected in Railway
- [ ] Auto-deploy is enabled (if available)
- [ ] Manual redeploy attempted (if auto-deploy not working)

