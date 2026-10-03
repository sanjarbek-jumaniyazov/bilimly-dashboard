import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MINI_APP_URL = os.getenv("MINI_APP_URL", "")

# When true, the API accepts an X-Debug-Telegram-Id header instead of a real,
# signed Telegram initData payload. Only for local development in a regular
# browser (e.g. testing the mini app before wiring it up inside Telegram) —
# never enable this on a public deployment.
DEBUG_AUTH = os.getenv("DEBUG_AUTH", "false").lower() == "true"

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "bot.db"))
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

QUIZ_LENGTH = 7  # questions per daily quiz session
