#!/bin/bash
# Run this script AFTER creating HOS-Storefront service in Railway dashboard

set -e

echo "🚀 Setting up HOS-Storefront service deployment..."
echo ""

cd "$(dirname "$0")"

# Check if service exists
echo "📋 Linking to HOS-Storefront service..."
railway service link HOS-Storefront || {
    echo "❌ Could not link to HOS-Storefront service"
    echo "Please make sure you've created the service in Railway dashboard first"
    echo "Run: railway open"
    exit 1
}

echo "✅ Linked to HOS-Storefront service"
echo ""

# Verify current service
echo "📊 Current service status:"
railway status
echo ""

# Set environment variables
echo "📋 Setting environment variables..."
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app"
railway variables --set "NODE_ENV=production"

echo ""
echo "✅ Environment variables set:"
railway variables | grep -E "NEXT_PUBLIC|NODE_ENV" || echo "   (Check Railway dashboard)"
echo ""

# Deploy
echo "🚀 Deploying Next.js frontend..."
echo "This may take 3-5 minutes..."
echo ""

railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 Check deployment status:"
echo "   railway logs"
echo ""
echo "🌐 Your frontend will be available at:"
railway domain 2>&1 | head -3 || echo "   (Check Railway dashboard for URL)"
echo ""
echo "💡 Next steps:"
echo "   1. Wait for deployment to complete (check logs: railway logs)"
echo "   2. Visit the URL from railway domain"
echo "   3. Test the frontend functionality"

