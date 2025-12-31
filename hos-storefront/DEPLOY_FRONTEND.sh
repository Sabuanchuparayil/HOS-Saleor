#!/bin/bash
set -e

echo "🚀 Deploying Next.js Frontend to Railway..."
echo ""

cd "$(dirname "$0")"

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed."
    echo "Install it with: npm i -g @railway/cli"
    exit 1
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway."
    echo "Please run: railway login"
    exit 1
fi

echo "✅ Railway CLI is ready"
echo ""

# Show current status
echo "📊 Current Railway Status:"
railway status
echo ""

# Check if we need to create a new service
read -p "Do you want to create a new service for the frontend? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Creating new service for frontend..."
    railway service create --name "HOS-Storefront" || {
        echo "⚠️  Service might already exist, continuing..."
    }
    railway service link HOS-Storefront || {
        echo "⚠️  Could not link service automatically"
        echo "Please run: railway service link HOS-Storefront"
    }
fi

echo ""
echo "📋 Setting environment variables..."

# Set environment variables
railway variables --set "NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
railway variables --set "NODE_ENV=production"

# Get domain for NEXT_PUBLIC_SITE_URL
DOMAIN=$(railway domain 2>/dev/null | head -1 | awk '{print $NF}' || echo "hos-marketplaceweb-production.up.railway.app")
railway variables --set "NEXT_PUBLIC_SITE_URL=https://${DOMAIN}"

echo ""
echo "✅ Environment variables set:"
railway variables | grep -E "NEXT_PUBLIC|NODE_ENV" || echo "   (Check Railway dashboard)"
echo ""

echo "🚀 Deploying to Railway..."
echo "This may take a few minutes..."
echo ""

# Deploy
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Check deployment:"
echo "   railway logs"
echo ""
echo "🌐 Your app URL:"
railway domain 2>&1 | head -3 || echo "   (Check Railway dashboard)"

