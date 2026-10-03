"""Live lookup of the Mini App URL.

The public URL comes from a free cloudflared quick tunnel, which changes every
time the tunnel is recycled. The watchdog writes the fresh URL into .env; the
bot must pick it up *without* a restart, so nothing in the bot caches the
value — every caller asks this module for the current URL.
"""

from __future__ import annotations

from dotenv import dotenv_values

from bot.config import BASE_DIR

ENV_FILE = BASE_DIR / ".env"


def current_mini_app_url() -> str:
    try:
        return (dotenv_values(ENV_FILE).get("MINI_APP_URL") or "").strip()
    except OSError:
        return ""
