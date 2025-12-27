# Debug Deployment Failure - Healthcheck Issues

## Current Issue

The deployment is failing with "Healthcheck failed!" which means:
1. The application is not starting, OR
2. The healthcheck endpoint is not responding, OR
3. The healthcheck path is still incorrect

## Critical Checks

### 1. Healthcheck Configuration (MOST IMPORTANT)

From your screenshot, the healthcheck is still failing. You MUST configure it in Railway Dashboard:

**Railway Dashboard → Saleor Service → Settings → Healthcheck:**
- **Path**: `/health/` (NOT `/graphql/`)
- **Timeout**: `300` seconds
- **Save**

The `railway.toml` file alone may not be enough - Railway often requires dashboard configuration.

### 2. Check Deployment Logs (Not Build Logs)

The screenshot shows "Build Logs" tab. You need to check **"Deploy Logs"** to see:
- Application startup errors
- Migration failures
- Missing environment variable errors
- Port binding issues

**Steps:**
1. Railway Dashboard → Saleor Service → Latest Deployment
2. Click **"Deploy Logs"** tab (NOT "Build Logs")
3. Look for errors like:
   - "ERROR: SECRET_KEY is not set"
   - "ERROR: DATABASE_URL is not set"
   - Migration errors
   - Application crash errors

### 3. Verify ALL Required Variables Are Set

From your screenshot, I can see SECRET_KEY is set. Verify these are also set:

**In Railway Dashboard → Saleor Service → Variables:**
- ✅ `SECRET_KEY` (confirmed set)
- ⚠️ `ALLOWED_HOSTS` - Check if it's updated with your actual domain (not placeholder)
- ⚠️ `DEBUG` - Should be `False`
- ⚠️ `DATABASE_URL` - Should be auto-set by PostgreSQL
- ⚠️ `CELERY_BROKER_URL` - Should be set
- ⚠️ `CELERY_RESULT_BACKEND` - Should be set

### 4. Common Issues and Solutions

#### Issue: Healthcheck path is wrong
**Solution:** Configure in Dashboard → Settings → Healthcheck → Path: `/health/`

#### Issue: Application not starting
**Check Deploy Logs for:**
- Missing environment variables
- Database connection errors
- Migration failures
- Python errors

#### Issue: ALLOWED_HOSTS has placeholder
**Solution:** Update with actual Railway domain:
```bash
railway variables --set "ALLOWED_HOSTS=*.railway.app,your-actual-domain.railway.app"
```

## Step-by-Step Debugging

### Step 1: Configure Healthcheck in Dashboard
1. Railway Dashboard → Saleor Service → **Settings** tab
2. Scroll to **"Healthcheck"** section
3. Set **Path** to `/health/`
4. Set **Timeout** to `300`
5. **Save**

### Step 2: Check Deploy Logs
1. Railway Dashboard → Saleor Service → Latest Deployment
2. Click **"Deploy Logs"** tab
3. Scroll through logs looking for:
   - Startup messages
   - Error messages
   - Migration status

### Step 3: Verify Variables
1. Railway Dashboard → Saleor Service → **Variables** tab
2. Verify all required variables are present
3. Check ALLOWED_HOSTS doesn't have placeholder

### Step 4: Temporarily Disable Healthcheck
If the app seems to be starting but healthcheck fails:
1. Railway Dashboard → Saleor Service → Settings → Healthcheck
2. **Disable** healthcheck temporarily
3. Check if service becomes "Online"
4. If yes, re-enable with `/health/` path
5. If no, check deploy logs for startup errors

### Step 5: Check Application is Actually Running
If healthcheck is disabled and service is "Online":
- Test the health endpoint: `https://your-app.railway.app/health/`
- Test GraphQL: `https://your-app.railway.app/graphql/`

## Expected Startup Log Sequence

If everything is working, you should see in Deploy Logs:
```
=========================================
Starting Saleor application...
=========================================
Environment check passed:
  - SECRET_KEY: 8b67de9ff...
  - DATABASE_URL: postgresql://...
  - PORT: 8000

Running database migrations...
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying migration_name...
Migrations completed successfully!

Starting application server on port 8000...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If you see errors instead, that's what's preventing the app from starting.

## Next Steps

1. **FIRST**: Configure healthcheck in Dashboard (Path: `/health/`)
2. **SECOND**: Check Deploy Logs (not Build Logs) for startup errors
3. **THIRD**: Share the Deploy Logs output if you need help diagnosing

The build succeeded (image was built), but the deployment is failing because the app isn't starting or responding to healthcheck.

