from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.db import get_or_create_user, remember_welcome_message
from bot.mini_app_url import current_mini_app_url

router = Router()

WELCOME_TEXT = {
    "uz": (
        "Assalomu alaykum! 👋\n\n"
        "Bilimly — TSUE talabalari uchun fanlarni qisqa matnlar va testlar orqali "
        "tezroq o'rganish ilovasi (pilot versiya).\n\n"
        "Boshlash uchun pastdagi tugmani bosing."
    ),
    "ru": (
        "Здравствуйте! 👋\n\n"
        "Bilimly — приложение для студентов ТГЭУ, помогающее быстрее изучать "
        "предметы с помощью коротких текстов и тестов (пилотная версия).\n\n"
        "Нажмите кнопку ниже, чтобы начать."
    ),
    "en": (
        "Hello! 👋\n\n"
        "Bilimly is an app for TSUE students to learn subjects faster through "
        "short reading cards and quizzes (pilot version).\n\n"
        "Tap the button below to get started."
    ),
}

HELP_TEXT = {
    "uz": (
        "Bilimly haqida:\n"
        "Ilova ichida: kursingiz bo'yicha fanlarni tanlaysiz, har bir mavzuni "
        "qisqa matn orqali o'qiysiz, so'ng test topshirasiz.\n\n"
        "/start — ilovani ochish"
    ),
    "ru": (
        "О Bilimly:\n"
        "В приложении вы выбираете предметы своего курса, читаете короткие "
        "карточки по каждой теме, а затем проходите тест.\n\n"
        "/start — открыть приложение"
    ),
    "en": (
        "About Bilimly:\n"
        "In the app you pick subjects for your course year, read short cards "
        "for each theme, then take a quiz.\n\n"
        "/start — open the app"
    ),
}

NOT_CONFIGURED_TEXT = {
    "uz": (
        "Ilova hali ulanmagan: MINI_APP_URL muhit o'zgaruvchisi sozlanmagan. "
        "(Admin uchun: .env faylida MINI_APP_URL ni to'ldiring.)"
    ),
    "ru": (
        "Приложение ещё не подключено: переменная окружения MINI_APP_URL не "
        "задана. (Для администратора: заполните MINI_APP_URL в .env.)"
    ),
    "en": (
        "The app isn't connected yet: the MINI_APP_URL environment variable "
        "isn't set. (Admin: fill in MINI_APP_URL in .env.)"
    ),
}

APP_BUTTON_TEXT = {
    "uz": "📚 Ilovani ochish",
    "ru": "📚 Открыть приложение",
    "en": "📚 Open the app",
}


def _lang(user: dict) -> str:
    language = user.get("language")
    return language if language in ("uz", "ru", "en") else "uz"


def app_keyboard(language: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=APP_BUTTON_TEXT.get(language, APP_BUTTON_TEXT["uz"]),
                    web_app=WebAppInfo(url=url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    language = _lang(user)

    url = current_mini_app_url()
    if not url:
        await message.answer(NOT_CONFIGURED_TEXT[language])
        return

    sent = await message.answer(WELCOME_TEXT[language], reply_markup=app_keyboard(language, url))
    # Remembered so the button can be re-pointed in place if the URL changes.
    remember_welcome_message(sent.chat.id, sent.message_id, url)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await message.answer(HELP_TEXT[_lang(user)])
