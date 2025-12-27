#!/bin/bash

# Correct Railway CLI commands to set environment variables
# Run these commands one at a time, or source this script and call the functions

echo "Setting Railway environment variables..."
echo "Make sure you're in the correct directory and Railway project is linked"
echo ""

# Function to set a variable
set_var() {
    local var_name=$1
    local var_value=$2
    echo "Setting $var_name..."
    echo "$var_value" | railway variables --set "$var_name" 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $var_name set successfully"
    else
        echo "❌ Failed to set $var_name"
    fi
    echo ""
}

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "Generated SECRET_KEY: $SECRET_KEY"
echo ""

# Set variables using the correct Railway CLI syntax
# Note: Railway CLI syntax might vary, so try the interactive method if this doesn't work

echo "IMPORTANT: Railway CLI variable syntax may vary."
echo "Try these methods:"
echo ""
echo "Method 1: Interactive (Recommended)"
echo "  railway variables"
echo "  Then follow the prompts to add variables interactively"
echo ""
echo "Method 2: Using Railway Dashboard (Easiest)"
echo "  1. Go to Railway Dashboard → Saleor Service → Variables"
echo "  2. Click '+ New Variable'"
echo "  3. Enter name and value"
echo ""
echo "Method 3: Try these commands (if supported by your Railway CLI version):"
echo ""
echo "  echo '$SECRET_KEY' | railway variables --set SECRET_KEY"
echo "  echo '*.railway.app,your-app-name.railway.app' | railway variables --set ALLOWED_HOSTS"
echo "  echo 'False' | railway variables --set DEBUG"
echo ""
echo "For Redis variables, use the Dashboard method with these values:"
echo "  CELERY_BROKER_URL: \${{Redis.REDIS_URL}}"
echo "  CELERY_RESULT_BACKEND: \${{Redis.REDIS_URL}}"
echo ""

