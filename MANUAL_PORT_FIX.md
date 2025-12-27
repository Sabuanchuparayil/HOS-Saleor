# Manual PORT Fix - Step by Step Guide

The PORT variable isn't being expanded. Here's how to fix it manually.

## Option 1: Update railway.toml (RECOMMENDED)

Railway automatically sets PORT. We can use it directly in the startCommand.

**Go to Railway Dashboard:**
1. Railway Dashboard → Saleor Service → Settings tab
2. Look for "Config-as-code" or find where you can edit `railway.toml`
3. OR edit `railway.toml` in your code and push

**Update the startCommand in railway.toml to:**

```toml
[deploy]
startCommand = "PORT=${PORT:-8000} sh /app/start.sh"
healthcheckPath = "/health/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## Option 2: Hardcode Port in start.sh (SIMPLE)

Since Railway sets PORT automatically, we can hardcode 8000 as default:

**In start.sh, change this line:**
```bash
PORT_VAL="${PORT:-8000}"
```

**To:**
```bash
PORT_VAL="8000"
```

Then Railway's PORT environment variable will still be used if set, but we have a working default.

## Option 3: Use Railway Dashboard Start Command

1. Railway Dashboard → Saleor Service → Settings → Deploy
2. Find "Start Command" field
3. Set it to: `PORT=${PORT:-8000} sh /app/start.sh`
4. OR set it to: `python manage.py migrate --noinput && uvicorn saleor.asgi:application --host=0.0.0.0 --port=${PORT:-8000} --workers=2 --lifespan=off --ws=none --no-server-header --no-access-log --timeout-keep-alive=35 --timeout-graceful-shutdown=30 --limit-max-requests=10000`

## Option 4: Simplify - Hardcode Port (EASIEST)

Railway usually uses port 8000 or a port it assigns. Let's just hardcode 8000:

**Update start.sh line 21-22 from:**
```bash
PORT_VAL="${PORT:-8000}"
export PORT=$PORT_VAL
```

**To:**
```bash
PORT_VAL="8000"
```

Railway will override this if needed, but at least it will start.

## Quick Fix - What Port Does Railway Use?

Railway typically uses:
- Port **8000** as default
- Or a port specified by the `PORT` environment variable (which Railway sets automatically)

**Easiest manual fix:** Just hardcode port 8000 in start.sh since Railway will work with that.

