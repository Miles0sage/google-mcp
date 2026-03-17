#!/usr/bin/env python3
"""
NotebookLM Session Keep-Alive — pings NotebookLM every 30 min to prevent session expiry.

Google invalidates NotebookLM sessions after ~2-4 hours of inactivity.
This script makes a lightweight request using stored cookies to keep the session alive.

Usage:
    # One-shot ping:
    python3 notebooklm_keepalive.py

    # Cron (every 30 min):
    */30 * * * * cd /root/google-mcp && python3 notebooklm_keepalive.py >> /root/google-mcp/data/keepalive.log 2>&1
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

STORAGE_STATE = Path.home() / ".notebooklm" / "storage_state.json"
LOG_DIR = Path(__file__).parent / "data"


async def ping_notebooklm() -> dict:
    """Make a lightweight request to NotebookLM to keep session alive."""
    from playwright.async_api import async_playwright

    if not STORAGE_STATE.exists():
        return {"success": False, "error": "storage_state.json not found"}

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
    context = await browser.new_context(storage_state=str(STORAGE_STATE))

    try:
        page = await context.new_page()
        resp = await page.goto(
            "https://notebooklm.google.com/",
            wait_until="domcontentloaded",
            timeout=20000,
        )

        url = page.url
        status = resp.status if resp else 0

        if "accounts.google.com" in url:
            await browser.close()
            await pw.stop()
            return {
                "success": False,
                "error": "Session expired — redirected to login",
                "url": url,
            }

        # Session alive — save refreshed cookies
        await context.storage_state(path=str(STORAGE_STATE))

        await browser.close()
        await pw.stop()
        return {
            "success": True,
            "status": status,
            "url": url,
            "message": "Session alive, cookies refreshed",
        }

    except Exception as e:
        await browser.close()
        await pw.stop()
        return {"success": False, "error": str(e)}


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    result = asyncio.run(ping_notebooklm())

    status = "OK" if result["success"] else "FAIL"
    msg = result.get("message", result.get("error", ""))
    print(f"[{ts}] NotebookLM keepalive: {status} — {msg}")

    # Append to log file
    log_file = LOG_DIR / "keepalive.log"
    with open(log_file, "a") as f:
        f.write(json.dumps({"timestamp": ts, **result}) + "\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
