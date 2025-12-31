#!/bin/bash
# Quick deploy commands - Run these AFTER creating HOS-Storefront service in dashboard

cd /Users/apple/HOS-Saleor/hos-storefront

echo "🔗 Linking to HOS-Storefront service..."
railway service link HOS-Storefront

echo ""
echo "📊 Verifying service link..."
railway status

echo ""
echo "📋 Setting environment variables..."
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

echo ""
echo "✅ Environment variables set. Verifying..."
railway variables | grep -E "NEXT_PUBLIC|NODE_ENV"

echo ""
echo "🚀 Deploying Next.js frontend..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 To check deployment status:"
echo "   railway logs"
echo ""
echo "🌐 To get your URL:"
echo "   railway domain"

