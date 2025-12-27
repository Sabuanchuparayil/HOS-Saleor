#!/usr/bin/env python3
"""
Argument-safe uvicorn wrapper.

Why: some runtimes (or overridden start commands) pass a literal "$PORT" to uvicorn
and/or invoke commands without shell expansion. Also, shell wrappers can accidentally
word-split args. This Python wrapper preserves argv exactly and normalizes --port.
"""

from __future__ import annotations

import os
import sys


def _default_port() -> str:
    env_port = (os.environ.get("PORT") or "").strip()
    if env_port.isdigit():
        return env_port
    return "8000"


def _normalize_port_value(v: str) -> str:
    v = (v or "").strip()
    if v in ("", "$PORT") or not v.isdigit():
        return _default_port()
    return v


def main(argv: list[str]) -> int:
    args = list(argv)
    out: list[str] = []

    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--port="):
            out.append("--port=" + _normalize_port_value(a.split("=", 1)[1]))
            i += 1
            continue
        if a == "--port":
            # Only consume the next argument if it's not another flag (doesn't start with --)
            # This prevents consuming flags like --host, --workers, etc. as port values
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                nxt = args[i + 1]
                out.extend(["--port", _normalize_port_value(nxt)])
                i += 2  # Skip both --port and its value
            else:
                # No value provided or next arg is another flag - use default port
                out.extend(["--port", _default_port()])
                i += 1  # Only skip --port, don't consume next argument
            continue
        out.append(a)
        i += 1

    # stdout marker (no secrets)
    try:
        print(
            f"[uvicorn-wrapper] argv_in_len={len(args)} argv_out_len={len(out)} "
            f"PORT_env={'<unset>' if os.environ.get('PORT') is None else repr(os.environ.get('PORT'))}",
            flush=True,
        )
    except Exception:
        pass

    os.execvp("python3", ["python3", "-m", "uvicorn", *out])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


