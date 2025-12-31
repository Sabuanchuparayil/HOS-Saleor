#!/bin/bash
set -e

echo "🚀 Deploying House of Spells Storefront to Railway..."
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

# Check if linked to a project
if ! railway status &> /dev/null; then
    echo "📦 Linking to Railway project..."
    echo "Please select your project when prompted..."
    railway link
fi

echo ""
echo "📋 Setting environment variables..."

# Set environment variables using Railway CLI v4 syntax
railway variables --set NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/ 2>&1 || {
    echo "⚠️  Note: You may need to set variables manually in Railway dashboard"
    echo "   NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/"
}

railway variables --set NODE_ENV=production 2>&1 || {
    echo "⚠️  Note: You may need to set NODE_ENV manually"
}

# Get the domain for NEXT_PUBLIC_SITE_URL
DOMAIN=$(railway domain 2>/dev/null | head -1 | awk '{print $NF}' || echo "hos-marketplaceweb-production.up.railway.app")
railway variables --set NEXT_PUBLIC_SITE_URL=https://${DOMAIN} 2>&1 || {
    echo "⚠️  Note: You may need to set NEXT_PUBLIC_SITE_URL manually"
    echo "   NEXT_PUBLIC_SITE_URL=https://${DOMAIN}"
}

echo ""
echo "🚀 Deploying to Railway..."
echo ""

# Deploy
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 Check deployment status:"
echo "   railway logs"
echo ""
echo "🌐 Your app will be available at:"
railway domain 2>&1 | head -3 || echo "   (Check Railway dashboard for URL)"

