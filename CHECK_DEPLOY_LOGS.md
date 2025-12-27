# Check Deploy Logs - Application Not Starting

## Current Status

✅ **Build:** Successful (image built correctly)
✅ **Healthcheck Path:** `/health/` (configured correctly)
✅ **ALLOWED_HOSTS:** `saleor-sabu.up.railway.app` (configured correctly)
❌ **Application:** Not starting (healthcheck fails with "service unavailable")

## The Problem

The build completes successfully, but the application isn't starting. The healthcheck fails because there's no application responding on the `/health/` endpoint.

## Critical: Check Deploy Logs

You're currently looking at **Build Logs**, but you need to check **Deploy Logs** to see why the application isn't starting.

### Steps:

1. **Railway Dashboard** → **Saleor Service** → **Latest Deployment**
2. Click the **"Deploy Logs"** tab (NOT "Build Logs")
3. Look for:
   - Startup messages from `start.sh`
   - Error messages
   - Migration failures
   - Application crash errors

## What to Look For in Deploy Logs

### If Application Starts Successfully:
You should see something like:
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
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Common Errors You Might See:

#### 1. Missing Environment Variables
```
ERROR: SECRET_KEY is not set - this is required!
```
**Fix:** Verify SECRET_KEY is set in Variables

#### 2. Database Connection Error
```
django.db.utils.OperationalError: could not connect to server
```
**Fix:** Check DATABASE_URL is set correctly

#### 3. Migration Failure
```
ERROR: Migrations failed!
django.db.migrations.exceptions.MigrationSchemaMissing
```
**Fix:** Check database connection and permissions

#### 4. Python Import Error
```
ModuleNotFoundError: No module named 'xxx'
```
**Fix:** Check dependencies are installed correctly

#### 5. Port Binding Error
```
ERROR: [Errno 98] Address already in use
```
**Fix:** Railway handles this automatically, but check if PORT is set

#### 6. Application Crash
```
Traceback (most recent call last):
  File ...
```
**Fix:** Check the traceback for the specific error

## Quick Troubleshooting Steps

### Step 1: Check Deploy Logs
- Go to Deploy Logs tab
- Scroll through the logs
- Look for ERROR messages or tracebacks

### Step 2: Verify All Variables
From your Variables tab, ensure these are set:
- ✅ SECRET_KEY
- ✅ DATABASE_URL (should be auto-set)
- ✅ ALLOWED_HOSTS (✅ confirmed: `saleor-sabu.up.railway.app`)
- ✅ DEBUG
- ✅ CELERY_BROKER_URL
- ✅ CELERY_RESULT_BACKEND

### Step 3: Check Database Connection
If migrations are failing:
- Verify PostgreSQL service is "Online"
- Check DATABASE_URL is correct
- Ensure database is accessible

### Step 4: Temporarily Disable Healthcheck
To see if app starts without healthcheck pressure:
1. Railway Dashboard → Saleor Service → Settings → Deploy
2. Disable healthcheck temporarily
3. Redeploy
4. Check if service becomes "Online"
5. If yes, re-enable healthcheck

## Next Steps

1. **Check Deploy Logs** - This is the most important step!
2. **Share the error messages** from Deploy Logs if you need help
3. **Fix the specific error** preventing the app from starting
4. **Redeploy** after fixing

The build is working correctly - the issue is in the application startup phase, which is shown in Deploy Logs, not Build Logs!

