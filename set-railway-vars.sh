#!/bin/bash

# Script to help set Railway environment variables
# This generates the commands you can run to set variables in Railway

echo "=========================================="
echo "Railway Variables Setup Helper"
echo "=========================================="
echo ""

# Generate SECRET_KEY
echo "1. Generate SECRET_KEY:"
SECRET_KEY=$(openssl rand -hex 32)
echo "   Generated SECRET_KEY: $SECRET_KEY"
echo ""
echo "   Railway CLI command:"
echo "   railway variables set SECRET_KEY=$SECRET_KEY"
echo ""

# Get Railway app name (you'll need to replace this)
echo "2. Set ALLOWED_HOSTS (replace 'your-app-name' with your actual Railway app name):"
echo "   railway variables set ALLOWED_HOSTS=\"*.railway.app,your-app-name.railway.app\""
echo ""

echo "3. Set DEBUG:"
echo "   railway variables set DEBUG=False"
echo ""

echo "4. Set Celery variables (if you have Redis service):"
echo "   railway variables set CELERY_BROKER_URL='\${{Redis.REDIS_URL}}'"
echo "   railway variables set CELERY_RESULT_BACKEND='\${{Redis.REDIS_URL}}'"
echo ""

echo "5. Set security variables:"
echo "   railway variables set SECURE_SSL_REDIRECT=True"
echo "   railway variables set SESSION_COOKIE_SECURE=True"
echo "   railway variables set CSRF_COOKIE_SECURE=True"
echo ""

echo "=========================================="
echo "All Commands (Copy and run these):"
echo "=========================================="
echo ""
echo "railway variables set SECRET_KEY=$SECRET_KEY"
echo "railway variables set ALLOWED_HOSTS=\"*.railway.app,your-app-name.railway.app\""
echo "railway variables set DEBUG=False"
echo "railway variables set CELERY_BROKER_URL='\${{Redis.REDIS_URL}}'"
echo "railway variables set CELERY_RESULT_BACKEND='\${{Redis.REDIS_URL}}'"
echo "railway variables set SECURE_SSL_REDIRECT=True"
echo "railway variables set SESSION_COOKIE_SECURE=True"
echo "railway variables set CSRF_COOKIE_SECURE=True"
echo ""
echo "Note: Replace 'your-app-name' with your actual Railway app domain name"
echo ""

