# Railway Deployment Checklist

## ✅ Pre-Deployment (Completed)

- [x] Environment variables configured
- [x] Railway CLI installed and logged in
- [x] Project linked to "Hos_Saleor"
- [x] Build configuration files ready (`railway.toml`, `railway.json`)
- [x] Package.json scripts configured

## 📋 Action Required: Create Service in Dashboard

**Open Railway Dashboard:** https://railway.app/dashboard

1. Navigate to project: **"Hos_Saleor"**
2. Click **"+ New"** button
3. Select **"Empty Service"**
4. Name: **"HOS-Storefront"**
5. Click **"Create"**

## 🚀 After Service Creation - Run These Commands

```bash
cd hos-storefront

# 1. Link to the new service
railway service link HOS-Storefront

# 2. Verify you're on the right service (should show HOS-Storefront)
railway status

# 3. Set environment variables
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

# 4. Deploy
railway up
```

**Or use the automated script:**
```bash
./QUICK_DEPLOY_COMMANDS.sh
```

## 📊 Post-Deployment Verification

- [ ] Check deployment logs: `railway logs`
- [ ] Get deployment URL: `railway domain`
- [ ] Visit the URL in browser
- [ ] Test homepage loads
- [ ] Test product listing page
- [ ] Verify GraphQL queries work
- [ ] Test cart functionality
- [ ] Check mobile responsiveness

## 🔍 Troubleshooting

### Service Not Found
- Make sure you created "HOS-Storefront" in the dashboard
- Check service name matches exactly (case-sensitive)

### Build Fails
- Check logs: `railway logs`
- Verify Node.js version (should be 20.x)
- Check `package.json` build scripts

### Environment Variables Not Working
- Verify with: `railway variables`
- Make sure variables start with `NEXT_PUBLIC_` for client-side access

## 📝 Quick Reference

**Check status:**
```bash
railway status
```

**View logs:**
```bash
railway logs
```

**Get URL:**
```bash
railway domain
```

**Open dashboard:**
```bash
railway open
```

