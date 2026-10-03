from __future__ import annotations

import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.auth import TelegramUser, get_current_telegram_user
from bot.config import BASE_DIR
from bot.db import (
    get_admin_stats,
    get_admin_user_detail,
    get_admin_users,
    get_admin_subject_stats,
    get_or_create_user,
    get_quiz_questions,
    get_user,
    get_user_progress_summary,
    init_db,
    list_majors,
    list_subjects_for_user,
    list_themes_for_subject,
    submit_quiz,
    update_user_profile,
)
from bot.seed import seed_all

logger = logging.getLogger("bilimly")
logging.basicConfig(level=logging.INFO)

WEBAPP_DIR = BASE_DIR / "webapp"

# If database setup fails, the app keeps running and the error is shown
# at /healthz instead of crashing every request with a 500.
STARTUP_ERROR: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global STARTUP_ERROR
    try:
        init_db()
        seed_all()
        logger.info("Database initialised and seeded")
    except Exception as exc:  # noqa: BLE001
        STARTUP_ERROR = f"{type(exc).__name__}: {exc}"
        logger.exception("Startup failed")
    yield


app = FastAPI(title="Bilimly API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProfileUpdate(BaseModel):
    full_name: str
    course_year: int
    faculty: str
    major_id: int
    language: str
    group_name: str


class QuizAnswer(BaseModel):
    question_id: int
    selected_index: int


class QuizSubmit(BaseModel):
    answers: list[QuizAnswer]


@app.get("/healthz")
def healthz():
    """Used by scripts/watchdog.sh and for diagnosing deploy problems."""
    return {
        "ok": STARTUP_ERROR is None,
        "startup_error": STARTUP_ERROR,
        "webapp_found": WEBAPP_DIR.is_dir(),
    }


@app.get("/api/debug/headers")
def debug_headers(request: Request):
    """Debug endpoint — only available when DEBUG_AUTH is enabled."""
    from bot.config import DEBUG_AUTH

    if not DEBUG_AUTH:
        raise HTTPException(status_code=404, detail="Not found")
    headers = dict(request.headers)
    return {
        "debug_auth_enabled": DEBUG_AUTH,
        "headers": {
            k: v
            for k, v in headers.items()
            if k.lower() in ["x-telegram-init-data", "x-debug-telegram-id"]
        },
    }


@app.get("/api/majors")
def api_list_majors():
    return list_majors()


@app.get("/api/me")
def api_get_me(tg_user: TelegramUser = Depends(get_current_telegram_user)):
    user = get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    return user


@app.put("/api/me")
def api_update_me(
    payload: ProfileUpdate, tg_user: TelegramUser = Depends(get_current_telegram_user)
):
    get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    try:
        return update_user_profile(
            telegram_id=tg_user.telegram_id,
            full_name=payload.full_name,
            course_year=payload.course_year,
            faculty=payload.faculty,
            major_id=payload.major_id,
            language=payload.language,
            group_name=payload.group_name,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


def _require_onboarded(tg_user: TelegramUser) -> dict:
    user = get_user(tg_user.telegram_id)
    if not user or not user["is_onboarded"]:
        raise HTTPException(status_code=403, detail="Profile not completed")
    return user


@app.get("/api/subjects")
def api_list_subjects(tg_user: TelegramUser = Depends(get_current_telegram_user)):
    user = _require_onboarded(tg_user)
    return list_subjects_for_user(
        user["major_id"], user["course_year"], language=user["language"]
    )


@app.get("/api/subjects/{subject_id}/themes")
def api_list_themes(
    subject_id: int, tg_user: TelegramUser = Depends(get_current_telegram_user)
):
    user = get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    return list_themes_for_subject(subject_id, user_id=user["id"], language=user["language"])


@app.get("/api/themes/{theme_id}/quiz")
def api_get_quiz(theme_id: int, tg_user: TelegramUser = Depends(get_current_telegram_user)):
    user = get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    return get_quiz_questions(theme_id, language=user["language"], user_id=user["id"])


@app.post("/api/themes/{theme_id}/quiz/submit")
def api_submit_quiz(
    theme_id: int,
    payload: QuizSubmit,
    tg_user: TelegramUser = Depends(get_current_telegram_user),
):
    user = get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    answers = [a.model_dump() for a in payload.answers]
    return submit_quiz(user["id"], theme_id, answers, language=user["language"])


@app.get("/api/progress")
def api_get_progress(tg_user: TelegramUser = Depends(get_current_telegram_user)):
    user = get_or_create_user(tg_user.telegram_id, tg_user.username, tg_user.full_name)
    return get_user_progress_summary(user["id"])


# --- Admin Dashboard Endpoints ------------------------------------------------


def _verify_admin(
    password: str = Query(""),
    x_admin_password: Optional[str] = Header(None),
) -> str:
    """Verify admin password.

    Accepts the X-Admin-Password header (preferred) or ?password= in the URL
    (kept so the current dashboard keeps working).
    """
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    supplied = x_admin_password or password or ""
    if not admin_password or not secrets.compare_digest(supplied, admin_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return supplied


@app.get("/api/admin/stats")
def api_admin_stats(password: str = Depends(_verify_admin)):
    """Get overall dashboard statistics."""
    return get_admin_stats()


@app.get("/api/admin/users")
def api_admin_users(
    password: str = Depends(_verify_admin),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get user list with activity stats."""
    return get_admin_users(limit=limit, offset=offset)


@app.get("/api/admin/users/{user_id}")
def api_admin_user_detail(user_id: int, password: str = Depends(_verify_admin)):
    """Get detailed activity for a specific user."""
    result = get_admin_user_detail(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@app.get("/api/admin/subjects")
def api_admin_subject_stats(password: str = Depends(_verify_admin)):
    """Get popular subjects and themes statistics."""
    return get_admin_subject_stats()


# --- Static web app -------------------------------------------------------------


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response


# Serves webapp/index.html, app.js, api.js, styles.css — must be mounted last
# so it doesn't shadow the /api/* routes above. If the folder is missing
# (e.g. not uploaded to GitHub), the API still starts instead of crashing.
if WEBAPP_DIR.is_dir():
    app.mount(
        "/",
        NoCacheStaticFiles(directory=str(WEBAPP_DIR), html=True),
        name="webapp",
    )
else:
    logger.warning("webapp folder not found at %s", WEBAPP_DIR)

    @app.get("/")
    def root_missing_webapp():
        return {
            "status": "API is running, but the webapp folder was not found",
            "expected_path": str(WEBAPP_DIR),
        }
