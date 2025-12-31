# Deployment Guide for House of Spells Storefront

## Railway Deployment

### Prerequisites
1. Railway account (https://railway.app)
2. Railway CLI installed (`npm i -g @railway/cli`)
3. Git repository connected

### Step 1: Install Railway CLI
```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
```

### Step 3: Initialize Railway Project
```bash
cd hos-storefront
railway init
```

### Step 4: Set Environment Variables

Required environment variables:

```bash
# Saleor API URL
railway variables set NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/

# Site URL (your Railway domain)
railway variables set NEXT_PUBLIC_SITE_URL=https://your-app-name.railway.app

# Node Environment
railway variables set NODE_ENV=production
```

### Step 5: Deploy
```bash
railway up
```

Or connect to GitHub for automatic deployments:
```bash
railway link
```

### Step 6: Configure Custom Domain (Optional)

1. Go to Railway dashboard
2. Select your service
3. Go to Settings > Domains
4. Add your custom domain
5. Update DNS records as instructed

### Step 7: Verify Deployment

1. Check build logs: `railway logs`
2. Visit your Railway URL
3. Test key features:
   - Homepage loads
   - Product listing works
   - GraphQL queries succeed
   - Images load correctly

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_SALEOR_API_URL` | Saleor GraphQL API endpoint | `https://hos-saleor-production.up.railway.app/graphql/` |
| `NEXT_PUBLIC_SITE_URL` | Your storefront URL | `https://hos-marketplaceweb-production.up.railway.app` |
| `NODE_ENV` | Environment mode | `production` |

## Troubleshooting

### Build Fails
- Check Node.js version (should be 20.x)
- Verify all dependencies are in package.json
- Check build logs: `railway logs`

### API Connection Issues
- Verify `NEXT_PUBLIC_SALEOR_API_URL` is correct
- Check CORS settings on Saleor backend
- Verify API is accessible

### Images Not Loading
- Check image domains in `next.config.ts`
- Verify `remotePatterns` configuration
- Check CDN settings if using one

## Post-Deployment Checklist

- [ ] Homepage loads correctly
- [ ] Product listing displays products
- [ ] Product detail pages work
- [ ] Cart functionality works
- [ ] Checkout flow works
- [ ] Search works
- [ ] User account pages work
- [ ] SEO meta tags are correct
- [ ] Sitemap is accessible
- [ ] robots.txt is accessible
- [ ] Images load correctly
- [ ] Animations work smoothly
- [ ] Mobile responsive design works

