from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.db import get_admin_stats, get_admin_users
import os

router = Router()

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
ADMIN_IDS = [6220653511]  # Add your Telegram ID here


def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("🔒 You are not authorized to access this command.")
        return

    stats = get_admin_stats()
    users = get_admin_users(limit=5)

    # Build stats message
    text = (
        "📊 <b>Bilimly Admin Dashboard</b>\n\n"
        f"👥 <b>Total Users:</b> {stats['total_users']}\n"
        f"✅ <b>Onboarded:</b> {stats['onboarded_users']}\n"
        f"📝 <b>Total Attempts:</b> {stats['total_attempts']}\n\n"
    )

    text += "<b>🔝 Top 5 Active Users:</b>\n"
    for user in users:
        if user["attempts_count"] > 0:
            text += (
                f"• {user['full_name']} (@{user['username'] or 'N/A'}): "
                f"{user['attempts_count']} attempts, "
                f"{user['accuracy']}% accuracy\n"
            )

    text += (
        f"\n🌐 <a href='https://dot-panels-pets-lucia.trycloudflare.com/admin.html'>"
        f"Open Full Dashboard</a>"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("🔒 You are not authorized to access this command.")
        return

    stats = get_admin_stats()
    text = (
        "📈 <b>Quick Stats</b>\n\n"
        f"👥 Users: {stats['total_users']}\n"
        f"✅ Onboarded: {stats['onboarded_users']}\n"
        f"📝 Attempts: {stats['total_attempts']}\n"
    )
    await message.answer(text, parse_mode="HTML")
