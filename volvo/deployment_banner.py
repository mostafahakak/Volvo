"""One-line startup banner for logs (Render, Docker, local)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone


def print_deployment_banner(component: str = "WSGI") -> None:
    """Print to stdout so platform logs show a successful deploy / process start."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    render = os.environ.get("RENDER")
    service = os.environ.get("RENDER_SERVICE_NAME", "n/a")
    external = os.environ.get("RENDER_EXTERNAL_URL", "")
    parts = [
        f"[Volvo API] {component} loaded — deploy active",
        ts + " UTC",
        f"RENDER={render!s}",
        f"service={service}",
    ]
    if external:
        parts.append(f"url={external}")
    line = " | ".join(parts)
    print(line, file=sys.stdout, flush=True)
