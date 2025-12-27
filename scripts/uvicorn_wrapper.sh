#!/bin/sh
set -eu

# This wrapper exists to harden deployments where the runtime passes a literal "$PORT"
# (for example, via a Procfile/Start Command evaluated without shell expansion).
# It rewrites non-numeric --port values to a safe default and then execs uvicorn via module.

DEFAULT_PORT="${PORT:-8000}"
if [ -z "${DEFAULT_PORT}" ]; then
  DEFAULT_PORT="8000"
fi

# --- debug marker (stdout only; no secrets) ---
echo "[uvicorn-wrapper] invoked argv=$* PORT_env='${PORT-<unset>}' DEFAULT_PORT='${DEFAULT_PORT}'"

fixed_args=""
while [ "$#" -gt 0 ]; do
  arg="$1"
  shift

  case "$arg" in
    --port=*)
      val="${arg#--port=}"
      case "$val" in
        ""|"\$PORT")
          fixed_args="$fixed_args --port=$DEFAULT_PORT"
          ;;
        *[!0-9]*)
          fixed_args="$fixed_args --port=$DEFAULT_PORT"
          ;;
        *)
          fixed_args="$fixed_args --port=$val"
          ;;
      esac
      ;;
    --port)
      next="${1-}"
      if [ "$#" -gt 0 ]; then shift; fi
      case "$next" in
        ""|"\$PORT")
          fixed_args="$fixed_args --port $DEFAULT_PORT"
          ;;
        *[!0-9]*)
          fixed_args="$fixed_args --port $DEFAULT_PORT"
          ;;
        *)
          fixed_args="$fixed_args --port $next"
          ;;
      esac
      ;;
    *)
      # Preserve other args (basic safe quoting for whitespace).
      # This builds a single string but ensures args with spaces survive when eval'd.
      esc="$(printf "%s" "$arg" | sed "s/'/'\\\\''/g")"
      fixed_args="$fixed_args '$esc'"
      ;;
  esac
done

# Use eval to expand the quoted string into discrete argv parts.
# shellcheck disable=SC2086
eval "exec python3 -m uvicorn $fixed_args"


