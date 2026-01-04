#!/bin/sh
set -eu

#region agent log (H5)
# Minimal marker so Railway logs prove whether start.sh is actually running.
# No secrets are logged.
echo "[start.sh] running (argv=$*) PORT_env='${PORT-<unset>}'"
#endregion

echo "========================================="
echo "Starting Saleor application..."
echo "========================================="

# Preflight: Saleor requires ALLOWED_CLIENT_HOSTS when DEBUG=False
# (saleor/settings.py raises ImproperlyConfigured otherwise).
# Security: Default to DEBUG=False (production mode) when DEBUG is not set.
# Only enable DEBUG when explicitly set to 'true' or '1'.
DEBUG_BOOL=$(python3 -c "import os; v=os.environ.get('DEBUG'); print('1' if v is not None and (str(v).lower()=='true' or str(v)=='1') else '0')")
# Check if ALLOWED_CLIENT_HOSTS is set and non-empty (after trimming whitespace)
ALLOWED_CLIENT_HOSTS_RAW="${ALLOWED_CLIENT_HOSTS-}"
ALLOWED_CLIENT_HOSTS_VAL="$(printf "%s" "$ALLOWED_CLIENT_HOSTS_RAW" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
ALLOWED_CLIENT_HOSTS_IS_SET="$([ -n "${ALLOWED_CLIENT_HOSTS_RAW}" ] && echo yes || echo no)"
ALLOWED_CLIENT_HOSTS_IS_NONEMPTY="$([ -n "$ALLOWED_CLIENT_HOSTS_VAL" ] && echo yes || echo no)"
echo "[start.sh] preflight DEBUG_BOOL=${DEBUG_BOOL} ALLOWED_CLIENT_HOSTS_env_set=${ALLOWED_CLIENT_HOSTS_IS_SET} ALLOWED_CLIENT_HOSTS_nonempty=${ALLOWED_CLIENT_HOSTS_IS_NONEMPTY}"
if [ "$DEBUG_BOOL" = "0" ] && [ -z "$ALLOWED_CLIENT_HOSTS_VAL" ]; then
    echo "ERROR: ALLOWED_CLIENT_HOSTS is required when DEBUG=False."
    echo ""
    echo "The variable is ${ALLOWED_CLIENT_HOSTS_IS_SET} but ${ALLOWED_CLIENT_HOSTS_IS_NONEMPTY} (empty or whitespace-only)."
    echo ""
    echo "Set Railway variable ALLOWED_CLIENT_HOSTS to a comma-separated list of hostnames (no https://)."
    echo "Example: ALLOWED_CLIENT_HOSTS=your-service.up.railway.app,localhost,127.0.0.1"
    echo ""
    echo "To set it via Railway CLI:"
    echo "  railway variables --set 'ALLOWED_CLIENT_HOSTS=*.railway.app,your-service.up.railway.app,localhost,127.0.0.1'"
    exit 1
fi

# Preflight: Saleor requires RSA_PRIVATE_KEY when DEBUG=False (JWT manager configuration).
RSA_KEY_SOURCE="none"

# Optional: allow base64-encoded key to avoid multiline env var issues on some platforms.
# If RSA_PRIVATE_KEY is missing/blank but RSA_PRIVATE_KEY_B64 is present, decode it.
RSA_PRIVATE_KEY_CLEAN="$(printf "%s" "${RSA_PRIVATE_KEY-}" | tr -d '\r' | xargs 2>/dev/null || true)"
if [ -z "$RSA_PRIVATE_KEY_CLEAN" ] && [ -n "${RSA_PRIVATE_KEY_B64-}" ]; then
    RSA_PRIVATE_KEY_DECODED="$(python3 -c "import os,base64; b=os.environ.get('RSA_PRIVATE_KEY_B64',''); print(base64.b64decode(b).decode('utf-8'))" 2>/dev/null || true)"
    if [ -n "$(printf "%s" "$RSA_PRIVATE_KEY_DECODED" | tr -d '\r' | xargs 2>/dev/null || true)" ]; then
        export RSA_PRIVATE_KEY="$RSA_PRIVATE_KEY_DECODED"
        RSA_PRIVATE_KEY_CLEAN="$(printf "%s" "${RSA_PRIVATE_KEY}" | tr -d '\r' | xargs 2>/dev/null || true)"
        RSA_KEY_SOURCE="b64"
    fi
fi
if [ -n "$RSA_PRIVATE_KEY_CLEAN" ]; then
    RSA_KEY_SOURCE="${RSA_KEY_SOURCE:-env}"
    if [ "$RSA_KEY_SOURCE" = "none" ]; then RSA_KEY_SOURCE="env"; fi
fi

# Safe diagnostics (do NOT print key): length + "looks like PEM" boolean.
# Calculate length from RSA_PRIVATE_KEY_CLEAN (after potential base64 decode) to ensure accuracy.
RSA_PRIVATE_KEY_LEN=$(printf "%s" "$RSA_PRIVATE_KEY_CLEAN" | wc -c | tr -d ' ')
# Check if the key looks like PEM format by checking if it starts with '-----BEGIN' (10 characters)
RSA_PRIVATE_KEY_FIRST_10=$(printf "%s" "$RSA_PRIVATE_KEY_CLEAN" | head -c 10)
if [ "$RSA_PRIVATE_KEY_FIRST_10" = "-----BEGIN" ]; then
    RSA_PRIVATE_KEY_IS_PEM="yes"
else
    RSA_PRIVATE_KEY_IS_PEM="no"
fi

echo "[start.sh] preflight RSA_PRIVATE_KEY_source=${RSA_KEY_SOURCE} RSA_PRIVATE_KEY_len=${RSA_PRIVATE_KEY_LEN} RSA_PRIVATE_KEY_looks_pem=${RSA_PRIVATE_KEY_IS_PEM}"
if [ "$DEBUG_BOOL" = "0" ] && [ "$RSA_PRIVATE_KEY_LEN" = "0" ]; then
    echo "ERROR: RSA_PRIVATE_KEY is required when DEBUG=False."
    echo "Set one of:"
    echo "  - RSA_PRIVATE_KEY (PEM private key, multiline), OR"
    echo "  - RSA_PRIVATE_KEY_B64 (base64 of the PEM private key)"
    exit 1
fi

# Check if required environment variables are set
if [ -z "${SECRET_KEY:-}" ]; then
    echo "ERROR: SECRET_KEY is not set - this is required!"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not set - this is required!"
    exit 1
fi

# Get PORT - Railway sets this, default to 8000
# Use Python to get PORT from environment to avoid expansion issues
# Handle empty/whitespace/non-numeric PORT (including literal '$PORT') by treating it as unset (use default 8000)
PORT_VAL=$(python3 -c "import os; port=(os.environ.get('PORT') or '').strip(); print(port if port.isdigit() else '8000')")
export PORT=$PORT_VAL

echo "Environment check passed:"
echo "  - SECRET_KEY: $(printf '%s' "${SECRET_KEY}" | cut -c1-10)..."
echo "  - DATABASE_URL: $(printf '%s' "${DATABASE_URL}" | cut -c1-30)..."
echo "  - PORT: $PORT_VAL"

echo ""
echo "Running database migrations..."
python3 manage.py migrate --noinput || {
    echo "ERROR: Migrations failed!"
    exit 1
}

# Explicitly run marketplace migrations (in case they weren't detected in the general migrate)
echo ""
echo "Running marketplace migrations explicitly..."
python3 manage.py migrate marketplace --noinput || {
    echo "WARNING: Marketplace migrations failed or already applied"
    # Don't exit - continue startup even if marketplace migrations have issues
}

echo ""
echo "Migrations completed successfully!"

# Optional: auto-configure Stripe gateway plugin (deprecated plugin) when keys are provided.
# This makes Stripe appear in `shop.availablePaymentGateways` without manual dashboard steps.
if [ -n "${STRIPE_PUBLIC_API_KEY:-}" ] && [ -n "${STRIPE_SECRET_API_KEY:-}" ]; then
    STRIPE_AUTO_CONFIGURE_BOOL=$(python3 -c "import os; v=(os.environ.get('STRIPE_AUTO_CONFIGURE','1') or '').strip().lower(); print('1' if v in ('1','true','yes','y') else '0')")
    if [ "$STRIPE_AUTO_CONFIGURE_BOOL" = "1" ]; then
        echo ""
        echo "Configuring Stripe gateway plugin (auto)..."
        python3 manage.py configure_stripe_gateway || {
            echo "ERROR: Failed to configure Stripe gateway plugin."
            exit 1
        }
    fi
fi

# Create superuser if environment variables are set (one-time operation)
if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo ""
    echo "Creating initial superuser (if not exists)..."
    python3 manage.py create_initial_superuser || {
        echo "WARNING: Failed to create superuser (may already exist)"
    }
fi

echo ""
echo "Starting application server on port $PORT_VAL..."

# Start uvicorn - use PORT_VAL (guaranteed to be a number from Python)
exec uvicorn saleor.asgi:application \
    --host=0.0.0.0 \
    --port="$PORT_VAL" \
    --workers=2 \
    --lifespan=off \
    --ws=none \
    --no-server-header \
    --no-access-log \
    --timeout-keep-alive=35 \
    --timeout-graceful-shutdown=30 \
    --limit-max-requests=10000
