#!/usr/bin/env python3
import json
import os
import re
import time
from pathlib import Path


LOG_PATH = Path("/Users/apple/Desktop/Saleor/.cursor/debug.log")
SESSION_ID = "debug-session"


def log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": SESSION_ID,
        "runId": os.environ.get("RUN_ID", "run1"),
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
    except Exception:
        # Never break the probe due to logging issues.
        pass


def read_text_if_exists(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    railway_toml = repo_root / "railway.toml"
    dockerfile = repo_root / "Dockerfile"
    procfile = repo_root / "Procfile"
    start_sh = repo_root / "start.sh"

    # #region agent log (H1/H2/H3/H4)
    log(
        "H0",
        "debug/entrypoint_probe.py:main",
        "Probe start",
        {
            "repoRoot": str(repo_root),
            "exists": {
                "railwayToml": railway_toml.exists(),
                "dockerfile": dockerfile.exists(),
                "procfile": procfile.exists(),
                "startSh": start_sh.exists(),
            },
        },
    )
    # #endregion

    proc = read_text_if_exists(procfile)
    rail = read_text_if_exists(railway_toml)
    dock = read_text_if_exists(dockerfile)

    # Hypothesis H1: Procfile is being used and contains a literal $PORT token.
    proc_has_dollar_port = "$PORT" in proc
    proc_has_uvicorn = "uvicorn" in proc
    # #region agent log (H1)
    log(
        "H1",
        "debug/entrypoint_probe.py:procfile",
        "Procfile scan",
        {
            "hasProcfile": procfile.exists(),
            "hasUvicorn": proc_has_uvicorn,
            "containsDollarPORT": proc_has_dollar_port,
            "firstLine": proc.splitlines()[0] if proc else "",
        },
    )
    # #endregion

    # Hypothesis H2: railway.toml startCommand overrides Dockerfile CMD (or is absent).
    start_cmd_match = re.search(r'^\s*startCommand\s*=\s*"(.*)"\s*$', rail, re.M)
    # #region agent log (H2)
    log(
        "H2",
        "debug/entrypoint_probe.py:railway_toml",
        "railway.toml scan",
        {
            "hasRailwayToml": railway_toml.exists(),
            "hasStartCommand": bool(start_cmd_match),
            "startCommand": start_cmd_match.group(1) if start_cmd_match else "",
            "builderDockerfile": bool(re.search(r'^\s*builder\s*=\s*"DOCKERFILE"\s*$', rail, re.M)),
        },
    )
    # #endregion

    # Hypothesis H3: Dockerfile CMD uses exec-form with $PORT (no shell expansion).
    cmd_line = ""
    for line in dock.splitlines():
        if line.strip().startswith("CMD "):
            cmd_line = line.strip()
    # #region agent log (H3)
    log(
        "H3",
        "debug/entrypoint_probe.py:dockerfile",
        "Dockerfile CMD scan",
        {
            "hasDockerfile": dockerfile.exists(),
            "cmdLine": cmd_line,
            "cmdContainsDollarPORT": "$PORT" in cmd_line,
            "cmdContainsStartSh": "start.sh" in cmd_line,
        },
    )
    # #endregion

    # Hypothesis H4: PORT env var is literally '$PORT' (misconfigured env var value).
    env_port = os.environ.get("PORT")
    # #region agent log (H4)
    log(
        "H4",
        "debug/entrypoint_probe.py:env",
        "Environment PORT sample",
        {
            "PORT_is_set": env_port is not None,
            "PORT_value_sample": env_port if env_port in (None, "", "$PORT") else "<redacted-nonempty>",
        },
    )
    # #endregion

    print("Entry-point probe:")
    print(f"- repo_root: {repo_root}")
    print(f"- Procfile present: {procfile.exists()}")
    if procfile.exists():
        print(f"  - contains 'uvicorn': {proc_has_uvicorn}")
        print(f"  - contains literal '$PORT': {proc_has_dollar_port}")
        if proc:
            print(f"  - first line: {proc.splitlines()[0]}")
    print(f"- railway.toml startCommand present: {bool(start_cmd_match)}")
    print(f"- Dockerfile CMD: {cmd_line or '<none found>'}")
    print(f"- Env PORT sample: {env_port!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


