# Next Steps After Setting Railway Variables

Great! You've successfully set all the required Railway environment variables. Here's what to do next:

## ✅ Variables Set Successfully

Based on your terminal output, these variables have been set:
- ✅ SECRET_KEY
- ✅ ALLOWED_HOSTS
- ✅ DEBUG
- ✅ CELERY_BROKER_URL
- ✅ CELERY_RESULT_BACKEND
- ✅ SECURE_SSL_REDIRECT
- ✅ SESSION_COOKIE_SECURE
- ✅ CSRF_COOKIE_SECURE

## Step 1: Verify Variables

Check that all variables are set correctly:

```bash
railway variables
```

Or verify on Railway:
- Railway Dashboard → Saleor Service → Variables tab
- Make sure all variables are listed

## Step 2: Configure Healthcheck in Railway Dashboard

**IMPORTANT:** This is critical for the deployment to succeed!

1. Go to **Railway Dashboard** → **Saleor Service** → **Settings** tab
2. Scroll to **"Healthcheck"** section
3. Set:
   - **Path**: `/health/` (change from `/graphql/`)
   - **Timeout**: `300` seconds
4. **Save** the settings

## Step 3: Redeploy the Service

After setting variables and configuring healthcheck:

1. Railway should **auto-redeploy**, OR
2. Go to **Railway Dashboard** → **Saleor Service** → **Deployments**
3. Click **"Redeploy"** or **"Deploy"**

## Step 4: Monitor Deployment

1. Watch the **deployment logs**:
   - Railway Dashboard → Saleor Service → Deployments
   - Click on the latest deployment
   - Click **"View Logs"**

2. Look for:
   - ✅ "Running database migrations..."
   - ✅ "Migrations completed. Starting application server..."
   - ✅ Application starting on port ${PORT}
   - ❌ Any errors (migration failures, missing variables, etc.)

## Step 5: Verify Healthcheck Passes

1. Check if the service status changes from "Build failed" to **"Online"**
2. The healthcheck should now pass using `/health/` endpoint
3. If it still fails, check the logs for startup errors

## Step 6: Test Your Application

Once deployed successfully:

1. **Health endpoint:**
   ```
   https://your-app.railway.app/health/
   ```
   Should return: `200 OK` with empty body

2. **GraphQL endpoint:**
   ```
   https://your-app.railway.app/graphql/
   ```
   Should show GraphQL interface or API documentation

3. **Admin dashboard:**
   ```
   https://your-app.railway.app/dashboard/
   ```
   Should show the login page (after creating a superuser)

## Step 7: Create Admin User

After successful deployment, create an admin user:

```bash
railway run python manage.py createsuperuser
```

Follow the prompts to:
- Enter email address
- Enter password
- Confirm password

## Step 8: (Optional) Populate Sample Data

To populate the database with sample products and data:

```bash
railway run python manage.py populatedb
```

## Troubleshooting

### If Deployment Still Fails

1. **Check logs** for specific errors
2. **Verify healthcheck** is set to `/health/` in Settings
3. **Check DATABASE_URL** is set (should be auto-set by PostgreSQL)
4. **Verify Redis** service is running (if using Celery)

### If Healthcheck Fails

1. Temporarily **disable healthcheck** in Settings
2. Check if service becomes "Online"
3. If yes, the app works - **re-enable healthcheck** with `/health/` path
4. If no, check logs for startup errors

### Common Issues

- **"Service unavailable"**: App not starting - check logs
- **"Connection refused"**: App crashed - check migration errors
- **"Timeout"**: App taking too long - check if migrations are slow

## Success Checklist

- [ ] All variables set in Railway
- [ ] Healthcheck configured to `/health/`
- [ ] Service redeployed
- [ ] Deployment logs show successful startup
- [ ] Service status is "Online"
- [ ] Health endpoint returns 200 OK
- [ ] GraphQL endpoint accessible
- [ ] Admin user created
- [ ] Application fully functional

## Getting Help

If you encounter issues:
1. Check the deployment logs
2. Review `RAILWAY_DEPLOYMENT_FIX.md` for troubleshooting
3. Check `RAILWAY_TROUBLESHOOTING.md` for common solutions
4. Verify all configuration files are correct

