# Bilimly (pilot)

A Telegram Mini App that turns teacher materials into Khan-Academy-style
lessons: short reading cards followed by a quiz, organized by faculty →
major → course year → subject → theme. Currently seeded with the full TSUE
Finance & Fintech (60410500) curriculum plus real lesson content for English
and Statistics.

## Architecture

- **`bot/`** — the Telegram bot (aiogram). It's a thin launcher: `/start`
  sends a button that opens the mini app.
- **`api/`** — FastAPI backend. Validates real Telegram Mini App auth
  (signed `initData`), serves the REST API, and also serves the frontend
  static files.
- **`webapp/`** — the mini app itself (vanilla HTML/CSS/JS, no build step).
- **`content/`** — curriculum + lesson JSON, loaded into SQLite on startup.
- **`scripts/generate_quiz.py`** — turns a teacher's raw material (`.txt`)
  into a lesson JSON (reading cards + quiz) via the Claude API.

## 1. Create your Telegram bot (one-time, ~2 minutes)

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot`, give it a name and a username ending in `bot`.
3. BotFather replies with a token like `123456789:AAH...`. Copy it.
4. Optionally set the bot's profile picture: `/setuserpic` in BotFather and
   upload `webapp/assets/logo.jpg` — this isn't settable via the Bot API, so
   it has to be done once by hand in BotFather.

## 2. Set up the project

```bash
cd telegram-exam-prep-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

```
BOT_TOKEN=123456789:AAH...        # from BotFather
ANTHROPIC_API_KEY=                # only needed for scripts/generate_quiz.py
MINI_APP_URL=                     # public HTTPS URL of the backend (see step 4)
DEBUG_AUTH=false                  # true only for local testing outside Telegram
```

## 3. Run the backend + bot

```bash
# Terminal 1 — API + webapp (same process serves both)
uvicorn api.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — the bot
python -m bot.main
```

On first run this creates `data/bot.db` and loads everything under
`content/`: the full curriculum (`curriculum.json`), plus lesson content
(`demo_lessons.json`, `lessons_statistics.json`, and any `lessons_*.json`
you add).

## 4. Running the pilot unattended (recommended)

Instead of the two terminals above, install the watchdog as a login service:

```bash
./scripts/install_service.sh
```

This runs `scripts/watchdog.sh` under launchd so it starts at login, is
restarted if it ever dies, and keeps the Mac from idle-sleeping
(`caffeinate`). The watchdog starts and supervises all three pieces (backend,
bot, cloudflared tunnel), restarts anything that stops answering, and when
the free tunnel URL changes it writes the new URL into `.env`. The bot
re-reads `.env` on its own (`bot/url_refresher.py`): it re-points the
Telegram menu button and edits the "Open the app" button on every /start
message it already sent, so students never hold a dead link.

Check on it any time with:

```bash
./scripts/status.sh
```

Two things the watchdog cannot fix by itself:

- **Lid closed / battery.** macOS sleeps when the lid is closed, and
  `caffeinate` only blocks sleep on AC power. Keep the Mac plugged in with
  the lid open, or run once: `sudo pmset -a disablesleep 1`.
- **The free tunnel is still temporary.** Recovery is automatic and takes
  ~15 seconds, but a student mid-quiz during that window sees an error.
  The permanent fix is a stable domain (a named Cloudflare Tunnel on your
  own domain, or hosting `api/` + `webapp/` on a small always-on server).

To uninstall: `./scripts/install_service.sh remove`.

## 5. Expose it over HTTPS by hand (manual alternative)

Telegram will only open a mini app over HTTPS. For quick testing:

```bash
./bin/cloudflared tunnel --url http://127.0.0.1:8000
```

This prints a `https://....trycloudflare.com` URL — put it in `.env` as
`MINI_APP_URL`; the bot picks it up within ~10 seconds, no restart needed. **Quick tunnels are temporary** (they can
drop after a while and the URL changes every restart) — fine for testing,
not for the real pilot. For that, deploy `api/` + `webapp/` to a small
always-on host (a cheap VPS, Railway, Fly.io, etc.) with a stable domain.

## How it works (student flow, inside the mini app)

1. Register once: name, course year, major, faculty, language, group.
2. Pick a subject for their course year (mandatory subjects first, then
   electives).
3. Pick a theme (chapter/topic) inside that subject.
4. Read a handful of short lesson cards.
5. Take a quiz on that theme — instant feedback + explanation per question.
6. Progress (best score, streak-free accuracy stats) is tracked per theme
   and visible on the profile screen.

## Adding real content from a teacher

1. Get the material as plain text.
2. Set `ANTHROPIC_API_KEY` in `.env`.
3. Run:
   ```bash
   python scripts/generate_quiz.py \
     --input materials/week3.txt \
     --subject-code STAT1305 \
     --theme "12-bob: Nonparametrik statistika" \
     --num-questions 6 \
     --output content/lessons_week3.json
   ```
   `--subject-code` must match a `code` in `content/curriculum.json`.
4. **Read through the generated file before trusting it** — the AI draft
   needs a human pass to catch wrong answers or ambiguous wording. One wrong
   answer and students stop trusting the app.
5. Restart the backend — it auto-loads every `content/lessons_*.json` file
   on startup, skipping themes that already have questions.

## Roadmap after the pilot validates

- Move off the temporary tunnel to a real always-on host with a stable URL
- Payme/Click checkout once you expand past your own pilot groups (keep the
  pilot free until then — see conversation notes on monetization strategy)
- Admin flow for teachers/TAs to upload materials without touching the CLI
- Postgres instead of SQLite once there's more than a couple hundred users
  (`DATABASE_URL` in `bot/config.py` is the only thing that needs to change)
- Localize lesson content per the student's chosen instruction language
