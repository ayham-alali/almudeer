"""
Small local debugging helper for hitting important API endpoints.

This is only meant for local development. It calls the running FastAPI
backend on http://127.0.0.1:8000 and prints status codes + short bodies.
"""

import urllib.request
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

# Insert the latest demo license key printed by the backend on startup.
DEMO_LICENSE_KEY = "MUDEER-B515-1AA1-034B"


def http_get(path: str, headers: Optional[dict] = None) -> None:
    url = BASE_URL + path
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"=== {path} -> {resp.status}")
            print(body[:400])
    except Exception as e:
        print(f"=== {path} -> ERROR: {e}")


def main() -> None:
    headers = {"X-License-Key": DEMO_LICENSE_KEY}

    # Basic health
    http_get("/health", {})

    # Dashboard endpoints
    http_get("/api/user/info", headers)
    http_get("/api/analytics/summary?days=30", headers)
    http_get("/api/analytics/chart?days=7", headers)
    http_get("/api/customers?limit=5", headers)
    http_get("/api/integrations/inbox?status=pending&limit=5", headers)
    http_get("/api/notifications/count", headers)


if __name__ == "__main__":
    main()


