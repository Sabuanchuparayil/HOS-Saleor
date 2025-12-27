# Final Deployment Checklist

## ✅ Completed Steps

- [x] Railway project created
- [x] PostgreSQL service added
- [x] Redis service added
- [x] Environment variables set (mostly)
- [x] Dockerfile configured for Railway
- [x] Startup script created
- [x] Railway.toml configured

## ⚠️ Action Required

### 1. Update ALLOWED_HOSTS (Critical)

Your ALLOWED_HOSTS currently has a placeholder. You need to update it with your actual Railway domain.

**Find your domain:**
- Railway Dashboard → Saleor Service → Settings
- Look for "Domain" section
- Or check your Railway project URL

**Update it:**
```bash
railway variables --set "ALLOWED_HOSTS=*.railway.app,your-actual-domain.railway.app"
```

Replace `your-actual-domain` with your real Railway domain (e.g., `saleor-production.up.railway.app`)

### 2. Configure Healthcheck (Critical)

Railway Dashboard → Saleor Service → Settings → Healthcheck:
- **Path**: `/health/` (change from `/graphql/`)
- **Timeout**: `300` seconds
- **Save**

### 3. Verify SECRET_KEY is Set

SECRET_KEY might not show in the variables list (it's masked for security). Verify it's set:
- Railway Dashboard → Saleor Service → Variables
- Look for SECRET_KEY in the list (value will be masked)

If not set, set it:
```bash
railway variables --set "SECRET_KEY=$(openssl rand -hex 32)"
```

## 🚀 Final Steps

1. **Redeploy** the service
2. **Monitor deployment logs**
3. **Check healthcheck** passes
4. **Test endpoints**

## 📋 Variables Status

From your `railway variables` output:

✅ Set correctly:
- ALLOWED_HOSTS (needs domain update)
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND
- CSRF_COOKIE_SECURE
- DATABASE_URL (auto-set)
- DEBUG

⚠️ Verify these are set (may be masked):
- SECRET_KEY
- SECURE_SSL_REDIRECT
- SESSION_COOKIE_SECURE

## 🔍 Quick Verification Commands

```bash
# Check all variables
railway variables

# Check if SECRET_KEY is set (will show masked if set)
railway variables | grep SECRET_KEY

# Check healthcheck configuration (via dashboard)
# Railway Dashboard → Service → Settings → Healthcheck
```

