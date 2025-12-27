# Railway Deployment Fix - Complete Guide

## Current Issues Identified

1. **Healthcheck still using `/graphql/`** - Railway may not be reading `railway.toml` for healthcheck settings
2. **Build/Deployment failing** - Application may not be starting properly
3. **Service unavailable** - Healthcheck fails because app isn't responding

## Step-by-Step Fix

### Step 1: Configure Healthcheck in Railway Dashboard

**CRITICAL:** Railway often requires healthcheck to be configured in the dashboard, not just in `railway.toml`.

1. Go to **Railway Dashboard** → **Saleor Service** → **Settings** tab
2. Scroll to **"Healthcheck"** section
3. Configure:
   - **Path**: `/health/` (change from `/graphql/`)
   - **Timeout**: `300` seconds
   - **Interval**: `10` seconds (default)
4. **Save** the settings
5. **Redeploy** the service

### Step 2: Verify Environment Variables

From the dashboard screenshot, ensure these are set in **Variables** tab:

**Required:**
- ✅ `DATABASE_URL` - Should be auto-set by PostgreSQL service
- ⚠️ `SECRET_KEY` - **MUST be set** (generate: `openssl rand -hex 32`)
- ⚠️ `ALLOWED_HOSTS` - Should include your Railway domain (e.g., `*.railway.app,your-app-name.railway.app`)

**Optional but recommended:**
- `DEBUG=False` (for production)
- `CELERY_BROKER_URL=${{Redis.REDIS_URL}}`
- `CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}`

### Step 3: Check Deployment Logs

1. Go to **Railway Dashboard** → **Saleor Service** → **Deployments**
2. Click on the latest deployment
3. Click **"View Logs"**
4. Look for:
   - Migration errors
   - Missing environment variable errors
   - Application startup errors
   - Port binding issues

### Step 4: Temporarily Disable Healthcheck (If Needed)

If the app is starting but healthcheck keeps failing:

1. **Railway Dashboard** → **Saleor Service** → **Settings** → **Healthcheck**
2. **Disable** healthcheck temporarily
3. Check if the service becomes "Online"
4. If yes, the app is working - re-enable healthcheck with `/health/` path
5. If no, check logs for startup errors

### Step 5: Verify Application is Running

Once healthcheck is configured correctly:

1. Check if service shows "Online" status
2. Access the health endpoint: `https://your-app.railway.app/health/`
   - Should return: `200 OK` with empty body
3. Access GraphQL endpoint: `https://your-app.railway.app/graphql/`
   - Should show GraphQL interface or API docs

## Current Configuration Files

### railway.toml
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### start.sh
- Runs database migrations before starting
- Validates required environment variables
- Starts uvicorn with Railway's PORT variable

## Troubleshooting

### If Healthcheck Still Fails After Configuration

1. **Check if app is actually starting:**
   - Disable healthcheck temporarily
   - See if service becomes "Online"
   - Check logs for startup errors

2. **Verify DATABASE_URL:**
   - Ensure PostgreSQL service is "Online"
   - Check that `DATABASE_URL` is set correctly
   - Test connection: `railway run python manage.py dbshell`

3. **Check SECRET_KEY:**
   - Must be set (not empty)
   - Generate new one if needed: `openssl rand -hex 32`

4. **Verify ALLOWED_HOSTS:**
   - Should include your Railway domain
   - Format: `*.railway.app,your-app-name.railway.app`

### Common Errors

**"Service unavailable"**
- App isn't starting
- Check logs for errors
- Verify environment variables

**"Connection refused"**
- App crashed on startup
- Check migration errors
- Verify database connection

**"Timeout"**
- App taking too long to start
- Increase healthcheck timeout
- Check if migrations are slow

## Next Steps After Successful Deployment

1. **Create Admin User:**
   ```bash
   railway run python manage.py createsuperuser
   ```

2. **Populate Sample Data (Optional):**
   ```bash
   railway run python manage.py populatedb
   ```

3. **Access Your Application:**
   - GraphQL: `https://your-app.railway.app/graphql/`
   - Dashboard: `https://your-app.railway.app/dashboard/`
   - Health: `https://your-app.railway.app/health/`

