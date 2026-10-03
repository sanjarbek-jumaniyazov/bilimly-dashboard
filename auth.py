from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from bot.config import BOT_TOKEN, DEBUG_AUTH


def _validate_init_data(init_data: str) -> dict | None:
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    return parsed


class TelegramUser:
    def __init__(self, telegram_id: int, username: str | None, full_name: str):
        self.telegram_id = telegram_id
        self.username = username
        self.full_name = full_name


def get_current_telegram_user(
    x_telegram_init_data: str = Header(default="", alias="X-Telegram-Init-Data"),
    x_debug_telegram_id: str = Header(default="", alias="X-Debug-Telegram-Id"),
    debug_id: str = "",  # Fallback for mobile WebViews that block custom headers
) -> TelegramUser:
    if x_telegram_init_data:
        parsed = _validate_init_data(x_telegram_init_data)
        if not parsed:
            raise HTTPException(status_code=401, detail="Invalid Telegram init data")
        user_json = parsed.get("user")
        if not user_json:
            raise HTTPException(status_code=401, detail="Missing user in init data")
        user = json.loads(user_json)
        full_name = " ".join(
            part for part in [user.get("first_name"), user.get("last_name")] if part
        )
        return TelegramUser(
            telegram_id=user["id"],
            username=user.get("username"),
            full_name=full_name or user.get("username") or "Student",
        )

    # Support both header and query param for debug mode (mobile WebView compatibility)
    if DEBUG_AUTH and (x_debug_telegram_id or debug_id):
        tg_id = x_debug_telegram_id or debug_id
        return TelegramUser(
            telegram_id=int(tg_id),
            username=None,
            full_name=f"Debug User {tg_id}",
        )

    raise HTTPException(status_code=401, detail="No Telegram authentication provided")
