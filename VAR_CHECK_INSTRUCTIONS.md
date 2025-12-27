# Railway Variables Check Script

A Node.js script to verify that all required Railway environment variables are properly set for Saleor deployment.

## Usage

### Option 1: Run Locally (Check what should be set)

```bash
# Run the script locally
node check-railway-vars.js

# Or using npm
npm run check-vars
```

This will check your local environment variables and show what's set and what's missing.

### Option 2: Run on Railway (Check actual Railway variables)

```bash
# Using Railway CLI (requires Railway CLI to be installed and logged in)
railway run node check-railway-vars.js

# Or using npm
npm run check-vars-railway
```

This will run the script inside Railway's environment and check the actual variables set in Railway.

## What the Script Checks

### Required Variables

- **SECRET_KEY** - Django secret key (must be set)
- **DATABASE_URL** - PostgreSQL connection string (auto-set by Railway)
- **ALLOWED_HOSTS** - Comma-separated list of allowed hosts

### Recommended Variables

- **DEBUG** - Should be `False` for production
- **CELERY_BROKER_URL** - Should reference Redis service
- **CELERY_RESULT_BACKEND** - Should reference Redis service
- **REDIS_URL** - Auto-set by Railway Redis service
- **SECURE_SSL_REDIRECT** - Should be `True` for production
- **SESSION_COOKIE_SECURE** - Should be `True` for production
- **CSRF_COOKIE_SECURE** - Should be `True` for production

## Setting Variables in Railway

### Using Railway Dashboard

1. Go to Railway Dashboard → Your Service → Variables tab
2. Click "+ New Variable"
3. Enter variable name and value
4. Save

### Using Railway CLI

```bash
# Set SECRET_KEY (generate a new one)
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Set ALLOWED_HOSTS
railway variables set ALLOWED_HOSTS="*.railway.app,your-app-name.railway.app"

# Set DEBUG
railway variables set DEBUG=False

# Set Celery variables (reference Redis service)
railway variables set CELERY_BROKER_URL='${{Redis.REDIS_URL}}'
railway variables set CELERY_RESULT_BACKEND='${{Redis.REDIS_URL}}'

# Set security variables
railway variables set SECURE_SSL_REDIRECT=True
railway variables set SESSION_COOKIE_SECURE=True
railway variables set CSRF_COOKIE_SECURE=True
```

### Using Railway Environment Files

You can also set variables using Railway's environment file feature, but for production deployments, using the dashboard or CLI is recommended.

## Troubleshooting

### Script shows errors for auto-set variables

Variables like `DATABASE_URL` and `REDIS_URL` are automatically set by Railway services. If the script shows them as missing when running locally, that's expected. Run the script on Railway to verify they're actually set.

### How to generate SECRET_KEY

```bash
# On macOS/Linux
openssl rand -hex 32

# Or using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Check variables in Railway Dashboard

1. Go to Railway Dashboard → Your Service → Variables
2. Verify all required variables are listed
3. Check that values are correct (they're masked for security)

## Next Steps

After verifying all variables are set:

1. **Redeploy** your service
2. **Check deployment logs** for any errors
3. **Verify healthcheck** is configured correctly (`/health/` endpoint)
4. **Test your application** endpoints

