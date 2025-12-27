# Healthcheck Configuration Fix

## Issue
Railway is still using `/graphql/` as the healthcheck path even after updating `railway.toml` to use `/health/`.

## Solutions

### Option 1: Configure Healthcheck in Railway Dashboard (Recommended)

Since Railway might not be reading `railway.toml` for healthcheck settings, configure it directly in the dashboard:

1. Go to Railway Dashboard → Your Service → Settings
2. Scroll to "Healthcheck" section
3. Set:
   - **Path**: `/health/`
   - **Timeout**: `300` seconds
4. Save and redeploy

### Option 2: Verify railway.toml is Being Read

The `railway.toml` file has been updated with:
```toml
healthcheckPath = "/health/"
healthcheckTimeout = 300
```

Make sure Railway is reading this file. If not, you may need to configure it in the dashboard instead.

### Option 3: Disable Healthcheck Temporarily

If the application is starting but healthcheck is still failing, you can temporarily disable it to see application logs:

1. Railway Dashboard → Service → Settings → Healthcheck
2. Disable healthcheck temporarily
3. Check deployment logs to see if the app starts
4. Re-enable healthcheck once the app is confirmed working

### Option 4: Check Application Logs

The real issue might be that the application isn't starting at all. Check:

1. Railway Dashboard → Service → Deployments → View Logs
2. Look for:
   - Migration errors
   - Missing environment variables (SECRET_KEY, DATABASE_URL)
   - Application startup errors
   - Port binding issues

### Required Environment Variables

Ensure these are set in Railway:
- `SECRET_KEY` (required - generate with: `openssl rand -hex 32`)
- `DATABASE_URL` (auto-set by Railway PostgreSQL service)
- `ALLOWED_HOSTS` (e.g., `*.railway.app,your-app-name.railway.app`)

### Testing Healthcheck Locally

If you want to test the healthcheck endpoint locally:
```bash
# After starting the app
curl http://localhost:8000/health/
# Should return: 200 OK with empty body
```

## Current Configuration

The `railway.toml` file is configured with:
- `healthcheckPath = "/health/"`
- `healthcheckTimeout = 300`

If Railway is still using `/graphql/`, configure it manually in the Railway dashboard.

