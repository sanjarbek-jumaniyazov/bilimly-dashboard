import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.db import init_db
from bot.handlers import router
from bot.seed import seed_all
from bot.url_refresher import refresh_loop


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is not set. Copy .env.example to .env and paste your "
            "token from @BotFather."
        )

    init_db()
    seed_all()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    # Keeps the menu button and previously sent "Open the app" buttons pointed
    # at the current Mini App URL without a restart (see bot/url_refresher.py).
    refresher = asyncio.create_task(refresh_loop(bot))
    try:
        await dispatcher.start_polling(bot)
    finally:
        refresher.cancel()


from fastapi import FastAPI

app = FastAPI()   # must be top-level and named exactly "app"

@app.get("/")
def home():
    return {"status": "ok"}
