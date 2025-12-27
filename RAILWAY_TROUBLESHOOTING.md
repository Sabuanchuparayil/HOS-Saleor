# Railway Deployment Troubleshooting

## Healthcheck Failed - Service Unavailable

If you see "Healthcheck failed!" errors, here are common causes and solutions:

### 1. Database Migrations Not Run

**Problem:** The application can't start because the database schema doesn't exist.

**Solution:** The `railway.toml` has been updated to run migrations automatically on startup. If migrations still fail:

- Check that `DATABASE_URL` is set correctly in Railway variables
- Verify PostgreSQL service is running
- Check application logs for migration errors

### 2. Missing Required Environment Variables

**Problem:** Saleor requires certain environment variables to start.

**Required Variables:**
```bash
SECRET_KEY=<your-secret-key>
DATABASE_URL=<auto-set-by-railway>
ALLOWED_HOSTS=*.railway.app,your-app-name.railway.app
```

**Solution:** 
- Go to Railway → Your Service → Variables
- Ensure all required variables are set
- Generate SECRET_KEY: `openssl rand -hex 32`

### 3. Application Not Starting

**Problem:** The application crashes on startup.

**Check Logs:**
- Go to Railway → Your Service → Deployments → View Logs
- Look for Python errors, import errors, or configuration issues

**Common Issues:**
- Missing dependencies (check if `uv sync` completed successfully)
- Invalid environment variable values
- Database connection errors

### 4. Healthcheck Timeout Too Short

**Problem:** Application takes longer than 100 seconds to start.

**Solution:** The healthcheck timeout has been increased to 200 seconds in `railway.toml`.

### 5. Port Configuration

**Problem:** Application not listening on the correct port.

**Solution:** 
- Railway automatically sets `$PORT` environment variable
- The startCommand uses `--port=$PORT` which should work
- If issues persist, check that Railway's PORT variable is being passed correctly

## Manual Migration Steps

If automatic migrations fail, run them manually:

1. Go to Railway → Your Service → Deployments
2. Click on the latest deployment
3. Open terminal/console
4. Run:
   ```bash
   python manage.py migrate
   ```

## Checking Application Status

1. **View Logs:**
   - Railway Dashboard → Service → Deployments → View Logs

2. **Check Environment Variables:**
   - Railway Dashboard → Service → Variables
   - Verify all required variables are set

3. **Test Database Connection:**
   ```bash
   railway run python manage.py dbshell
   ```

4. **Check if Application is Running:**
   ```bash
   railway run ps aux | grep uvicorn
   ```

## Common Error Messages

### "No such file or directory: manage.py"
- Ensure you're in the correct directory
- Check that the Dockerfile copied all files correctly

### "django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment variable"
- Set `SECRET_KEY` in Railway variables

### "django.db.utils.OperationalError: could not connect to server"
- Check `DATABASE_URL` is set
- Verify PostgreSQL service is running
- Check network connectivity

### "ModuleNotFoundError"
- Dependencies might not be installed correctly
- Check build logs for `uv sync` errors

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

