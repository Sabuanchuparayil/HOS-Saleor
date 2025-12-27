# Setting Railway Variables - Dashboard Method (RECOMMENDED)

Since Railway CLI syntax can be tricky, **using the Railway Dashboard is the easiest and most reliable method**.

## Step-by-Step: Set Variables in Railway Dashboard

### 1. Go to Railway Dashboard

1. Open [railway.app](https://railway.app)
2. Navigate to your project: **Saleor Commerce**
3. Click on the **Saleor** service (not Postgres or Redis)

### 2. Open Variables Tab

1. Click on the **"Variables"** tab (should be visible in the modal/service view)
2. You should see a list of existing variables

### 3. Add Required Variables

Click **"+ New Variable"** or **"Add Variable"** for each of these:

#### Required Variables:

1. **SECRET_KEY**
   - Name: `SECRET_KEY`
   - Value: Generate one with: `openssl rand -hex 32`
   - Or use this generated one: `8b67de9ff8bcde35ea5e6e87e7515af40d782cf2ae3753b1632c2e3c09f52f8c`
   - Click **Save**

2. **ALLOWED_HOSTS**
   - Name: `ALLOWED_HOSTS`
   - Value: `*.railway.app,your-app-name.railway.app`
   - **Important:** Replace `your-app-name` with your actual Railway app domain
   - To find your domain: Check Railway Dashboard → Service → Settings → Domain, or look at your Railway URL
   - Click **Save**

3. **DEBUG**
   - Name: `DEBUG`
   - Value: `False`
   - Click **Save**

#### Recommended Variables (if you have Redis):

4. **CELERY_BROKER_URL**
   - Name: `CELERY_BROKER_URL`
   - Value: `${{Redis.REDIS_URL}}`
   - Click **Save**

5. **CELERY_RESULT_BACKEND**
   - Name: `CELERY_RESULT_BACKEND`
   - Value: `${{Redis.REDIS_URL}}`
   - Click **Save**

#### Security Variables:

6. **SECURE_SSL_REDIRECT**
   - Name: `SECURE_SSL_REDIRECT`
   - Value: `True`
   - Click **Save**

7. **SESSION_COOKIE_SECURE**
   - Name: `SESSION_COOKIE_SECURE`
   - Value: `True`
   - Click **Save**

8. **CSRF_COOKIE_SECURE**
   - Name: `CSRF_COOKIE_SECURE`
   - Value: `True`
   - Click **Save**

### 4. Verify Variables Are Set

After adding all variables:
1. Scroll through the Variables list
2. Verify all variables are present
3. Check that values look correct (they'll be masked for security)

### 5. Redeploy

After setting variables:
1. Railway should auto-redeploy, OR
2. Go to **Deployments** tab
3. Click **"Redeploy"** or trigger a new deployment

## Quick Reference: Variable List

Copy this list to track what you've set:

- [ ] `SECRET_KEY` = `8b67de9ff8bcde35ea5e6e87e7515af40d782cf2ae3753b1632c2e3c09f52f8c`
- [ ] `ALLOWED_HOSTS` = `*.railway.app,your-app-name.railway.app`
- [ ] `DEBUG` = `False`
- [ ] `CELERY_BROKER_URL` = `${{Redis.REDIS_URL}}` (if you have Redis)
- [ ] `CELERY_RESULT_BACKEND` = `${{Redis.REDIS_URL}}` (if you have Redis)
- [ ] `SECURE_SSL_REDIRECT` = `True`
- [ ] `SESSION_COOKIE_SECURE` = `True`
- [ ] `CSRF_COOKIE_SECURE` = `True`

**Auto-set (no action needed):**
- ✅ `DATABASE_URL` (set by PostgreSQL service)
- ✅ `REDIS_URL` (set by Redis service, if added)

## Finding Your Railway App Domain

To find what to use for `ALLOWED_HOSTS`:

1. Railway Dashboard → Saleor Service → **Settings** tab
2. Look for **"Domain"** or **"Networking"** section
3. Your domain will be something like: `saleor-production.up.railway.app`
4. Use: `*.railway.app,saleor-production.up.railway.app` (replace with your actual domain)

Or check your Railway project URL - it usually contains the domain name.

## After Setting Variables

1. **Redeploy** the service
2. **Check deployment logs** for any errors
3. **Verify healthcheck** is set to `/health/` in Settings
4. **Test the application** once it's deployed

