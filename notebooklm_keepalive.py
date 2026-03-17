#!/usr/bin/env python3
"""
NotebookLM Session Keep-Alive — uses persistent Chrome profile to keep cookies alive.

Instead of throwaway contexts from storage_state.json, uses a real Chrome profile
directory that stores cookies natively (like a real browser). Sessions survive
much longer because the profile keeps all cookie state, not just the exported snapshot.

Cron:
    */30 * * * * cd /root/google-mcp && python3 notebooklm_keepalive.py >> /root/google-mcp/data/keepalive.log 2>&1
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = str(Path.home() / ".notebooklm" / "chrome-profile")
STORAGE_BACKUP = str(Path.home() / ".notebooklm" / "storage_state.json")
LOG_DIR = Path(__file__).parent / "data"


async def ping_notebooklm() -> dict:
    """Make a lightweight request using persistent browser profile."""
    os.makedirs(PROFILE_DIR, exist_ok=True)

    pw = await async_playwright().start()

    # Check if we need to seed profile from storage_state backup
    storage_path = Path(STORAGE_BACKUP)
    profile_cookies = Path(PROFILE_DIR) / "Default" / "Cookies"

    try:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            storage_state=str(storage_path) if (storage_path.exists() and not profile_cookies.exists()) else None,
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        )
    except Exception as e:
        await pw.stop()
        return {"success": False, "error": f"Browser launch failed: {e}"}

    try:
        page = context.pages[0] if context.pages else await context.new_page()
        resp = await page.goto(
            "https://notebooklm.google.com/",
            wait_until="domcontentloaded",
            timeout=20000,
        )

        url = page.url
        status = resp.status if resp else 0

        if "accounts.google.com" in url:
            await context.close()
            await pw.stop()
            return {
                "success": False,
                "error": "Session expired — redirected to login",
                "url": url,
            }

        # Scroll a bit to look human
        await page.evaluate("window.scrollTo(0, 200)")
        await page.wait_for_timeout(2000)

        # Save storage_state as backup
        try:
            await context.storage_state(path=STORAGE_BACKUP)
        except Exception:
            pass

        await context.close()
        await pw.stop()
        return {
            "success": True,
            "status": status,
            "url": url,
            "message": "Session alive, cookies refreshed in persistent profile",
        }

    except Exception as e:
        try:
            await context.close()
            await pw.stop()
        except Exception:
            pass
        return {"success": False, "error": str(e)}


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    result = asyncio.run(ping_notebooklm())

    status = "OK" if result["success"] else "FAIL"
    msg = result.get("message", result.get("error", ""))
    print(f"[{ts}] NotebookLM keepalive: {status} — {msg}")

    log_file = LOG_DIR / "keepalive.log"
    with open(log_file, "a") as f:
        f.write(json.dumps({"timestamp": ts, **result}) + "\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
