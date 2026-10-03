"""Keeps Telegram in sync with the current Mini App URL.

Runs inside the bot process. Every few seconds it re-reads MINI_APP_URL from
.env (the watchdog rewrites it whenever the tunnel is recycled). When the URL
changes it:

1. points the bot's global menu button (the button next to the message box)
   at the new URL, so every user has a working entry point immediately, and
2. edits the "Open the app" button on the last /start message of every chat
   so the buttons students already have stop pointing at the dead URL.

No bot restart is needed for a URL change.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import MenuButtonWebApp, WebAppInfo

from bot.db import (
    forget_welcome_message,
    get_user,
    list_welcome_messages_needing_url,
    mark_welcome_message_url,
)
from bot.handlers.start import APP_BUTTON_TEXT, app_keyboard
from bot.mini_app_url import current_mini_app_url

log = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 10


async def _set_menu_button(bot: Bot, url: str) -> bool:
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text=APP_BUTTON_TEXT["uz"].replace("📚 ", ""), web_app=WebAppInfo(url=url)
            )
        )
        log.info("menu button now points at %s", url)
        return True
    except (TelegramNetworkError, TelegramBadRequest) as exc:
        log.warning("could not set menu button: %s", exc)
        return False


async def _repoint_old_messages(bot: Bot, url: str) -> None:
    pending = list_welcome_messages_needing_url(url)
    if not pending:
        return
    log.info("re-pointing %d welcome message(s) at %s", len(pending), url)
    for item in pending:
        chat_id, message_id = item["chat_id"], item["message_id"]
        user = get_user(chat_id) or {}
        language = user.get("language") or "uz"
        while True:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=app_keyboard(language, url),
                )
                mark_welcome_message_url(chat_id, url)
            except TelegramRetryAfter as exc:
                await asyncio.sleep(exc.retry_after + 1)
                continue
            except TelegramForbiddenError:
                # User blocked the bot — nothing to update any more.
                forget_welcome_message(chat_id)
            except TelegramBadRequest as exc:
                text = str(exc).lower()
                if "not modified" in text:
                    mark_welcome_message_url(chat_id, url)
                elif "not found" in text or "can't be edited" in text:
                    forget_welcome_message(chat_id)
                else:
                    log.warning("edit failed for chat %s: %s", chat_id, exc)
            except TelegramNetworkError as exc:
                log.warning("network error editing chat %s: %s", chat_id, exc)
                return  # retried on the next tick
            break
        await asyncio.sleep(0.1)  # stay well under Telegram's rate limit


async def refresh_loop(bot: Bot) -> None:
    applied_url = ""
    while True:
        try:
            url = current_mini_app_url()
            if url and url != applied_url:
                log.info("Mini App URL changed: %r -> %r", applied_url, url)
                if await _set_menu_button(bot, url):
                    applied_url = url
            if url:
                await _repoint_old_messages(bot, url)
        except Exception:  # noqa: BLE001 — the loop must never die
            log.exception("url refresher tick failed")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
