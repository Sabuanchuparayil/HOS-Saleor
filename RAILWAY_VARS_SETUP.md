# Railway Variables Setup Guide

Based on the variables check script, here are the steps to set up all required Railway environment variables.

## Quick Setup Commands

### Step 1: Generate and Set SECRET_KEY

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set it in Railway
railway variables set SECRET_KEY=$SECRET_KEY
```

### Step 2: Set ALLOWED_HOSTS

Replace `your-app-name` with your actual Railway app domain:

```bash
railway variables set ALLOWED_HOSTS="*.railway.app,your-app-name.railway.app"
```

**To find your app name:**
- Go to Railway Dashboard → Your Service → Settings
- Look for the "Domain" or check your Railway URL
- Or use: `your-service-name.up.railway.app` format

### Step 3: Set DEBUG

```bash
railway variables set DEBUG=False
```

### Step 4: Set Celery Variables (if you have Redis)

```bash
railway variables set CELERY_BROKER_URL='${{Redis.REDIS_URL}}'
railway variables set CELERY_RESULT_BACKEND='${{Redis.REDIS_URL}}'
```

**Note:** The `${{Redis.REDIS_URL}}` syntax references the Redis service in Railway.

### Step 5: Set Security Variables

```bash
railway variables set SECURE_SSL_REDIRECT=True
railway variables set SESSION_COOKIE_SECURE=True
railway variables set CSRF_COOKIE_SECURE=True
```

## Using Railway Dashboard (Alternative Method)

If you prefer using the dashboard:

1. Go to **Railway Dashboard** → **Saleor Service** → **Variables** tab
2. Click **"+ New Variable"** for each variable
3. Enter the variable name and value
4. Save

### Variables to Set in Dashboard:

| Variable Name | Value | Required |
|--------------|-------|----------|
| `SECRET_KEY` | (Generate: `openssl rand -hex 32`) | ✅ Yes |
| `ALLOWED_HOSTS` | `*.railway.app,your-app-name.railway.app` | ✅ Yes |
| `DEBUG` | `False` | ⚠️ Recommended |
| `CELERY_BROKER_URL` | `${{Redis.REDIS_URL}}` | ⚠️ Recommended |
| `CELERY_RESULT_BACKEND` | `${{Redis.REDIS_URL}}` | ⚠️ Recommended |
| `SECURE_SSL_REDIRECT` | `True` | ⚠️ Recommended |
| `SESSION_COOKIE_SECURE` | `True` | ⚠️ Recommended |
| `CSRF_COOKIE_SECURE` | `True` | ⚠️ Recommended |

### Auto-Set Variables (No action needed):

These are automatically set by Railway services:
- `DATABASE_URL` - Set by PostgreSQL service
- `REDIS_URL` - Set by Redis service (if added)

## Verify Variables Are Set

After setting all variables, verify them:

```bash
# Run the check script on Railway
railway run node check-railway-vars.js
```

Or check in Railway Dashboard → Service → Variables tab.

## After Setting Variables

1. **Redeploy** your service to apply the new variables
2. **Check deployment logs** to ensure everything starts correctly
3. **Verify healthcheck** is configured (Path: `/health/`)
4. **Test your application** endpoints

## Troubleshooting

### SECRET_KEY already exists

If SECRET_KEY is already set but you want to regenerate it:
```bash
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

### Variables not showing up

- Make sure you're in the correct service
- Refresh the Railway dashboard
- Check that you saved the variables

### CELERY variables not working

Make sure you have a Redis service added to your Railway project. The `${{Redis.REDIS_URL}}` syntax only works if you have a service named "Redis" in your project.

