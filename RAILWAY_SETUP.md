# Railway Deployment Setup for Saleor

This repository is configured for deployment on Railway. The official Saleor repository has been set up with Railway-specific configurations.

## Configuration Files

- **railway.toml** - Railway deployment configuration with start command and health checks
- **Procfile** - Alternative process file for Railway (uses Railway's PORT variable)
- **Dockerfile** - Modified to use Railway's PORT environment variable

## Quick Setup on Railway

1. **Create a Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository: `https://github.com/Sabuanchuparayil/saleor`

2. **Add PostgreSQL Database**
   - In Railway dashboard, click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway automatically creates `DATABASE_URL` environment variable

3. **Add Redis Instance**
   - Click "+ New" → "Database" → "Add Redis"
   - Railway automatically creates `REDIS_URL` environment variable

4. **Configure Environment Variables**

   Go to your service → "Variables" tab and add:

   ```bash
   # Secret Key (generate with: openssl rand -hex 32)
   SECRET_KEY=<your-generated-secret-key>
   
   # Allowed Hosts (your Railway domain)
   ALLOWED_HOSTS=*.railway.app,your-app-name.railway.app
   
   # Debug mode (False for production)
   DEBUG=False
   
   # Celery Configuration (references Redis service)
   CELERY_BROKER_URL=${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
   
   # Static files
   STATIC_URL=/static/
   STATIC_ROOT=/app/static
   
   # Media files
   MEDIA_URL=/media/
   MEDIA_ROOT=/app/media
   
   # Site configuration
   SITE_NAME=My Saleor Store
   SITE_DOMAIN=your-app-name.railway.app
   
   # Security settings (for production)
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

   **Note:** `DATABASE_URL` and `REDIS_URL` are automatically set by Railway services.

5. **Deploy**
   - Railway will automatically deploy when you push to the connected branch
   - Or trigger a manual deploy from the dashboard

6. **Run Database Migrations**
   ```bash
   railway run python manage.py migrate
   # Or via Railway dashboard terminal
   python manage.py migrate
   ```

7. **Create Admin User**
   ```bash
   railway run python manage.py createsuperuser
   ```

8. **Access Your Application**
   - GraphQL API: `https://your-app-name.railway.app/graphql/`
   - Admin Dashboard: `https://your-app-name.railway.app/dashboard/`

## Important Notes

- This Saleor setup uses **uvicorn** (not gunicorn) as the ASGI server
- Python 3.12 is used
- The application uses **uv** for package management
- Railway's `PORT` environment variable is automatically used

## Git Remotes

This repository has two remotes configured:
- `origin` - Points to the official Saleor repository (https://github.com/saleor/saleor.git)
- `github` - Points to your repository (https://github.com/Sabuanchuparayil/saleor.git)

To push to your repository:
```bash
git push github main
```

## Additional Configuration

For production deployments, consider:
- Setting up email service (SMTP configuration)
- Configuring object storage (AWS S3, etc.) for media files
- Setting up payment gateway credentials
- Configuring monitoring and error tracking (Sentry, etc.)
- Setting up separate Celery worker services for background tasks

