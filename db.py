from __future__ import annotations

import datetime
import json
import random
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from bot.config import DATABASE_URL

SUPPORTED_LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"


def _lang(language: Optional[str]) -> str:
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def _loc(base: str, ru: Optional[str], en: Optional[str], language: Optional[str]) -> str:
    """Returns the field in the requested language, falling back to the
    default-language (Uzbek) value when no translation has been added yet."""
    lang = _lang(language)
    if lang == "ru" and ru:
        return ru
    if lang == "en" and en:
        return en
    return base


class Base(DeclarativeBase):
    pass


class Major(Base):
    __tablename__ = "majors"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(256))
    name_ru: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    faculty: Mapped[str] = mapped_column(String(256))
    faculty_ru: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    faculty_en: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    subjects: Mapped[list["Subject"]] = relationship(back_populates="major")

    def localized_name(self, language: Optional[str]) -> str:
        return _loc(self.name, self.name_ru, self.name_en, language)

    def localized_faculty(self, language: Optional[str]) -> str:
        return _loc(self.faculty, self.faculty_ru, self.faculty_en, language)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    major_id: Mapped[int] = mapped_column(ForeignKey("majors.id"))
    course_year: Mapped[int] = mapped_column(Integer)
    semester: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(256))
    name_ru: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_elective: Mapped[bool] = mapped_column(Boolean, default=False)
    track: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    major: Mapped["Major"] = relationship(back_populates="subjects")
    themes: Mapped[list["Theme"]] = relationship(back_populates="subject")

    def localized_name(self, language: Optional[str]) -> str:
        return _loc(self.name, self.name_ru, self.name_en, language)


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    title: Mapped[str] = mapped_column(String(256))
    title_ru: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    subject: Mapped["Subject"] = relationship(back_populates="themes")
    cards: Mapped[list["LessonCard"]] = relationship(
        back_populates="theme", order_by="LessonCard.order_index"
    )
    questions: Mapped[list["Question"]] = relationship(back_populates="theme")

    def localized_title(self, language: Optional[str]) -> str:
        return _loc(self.title, self.title_ru, self.title_en, language)


class LessonCard(Base):
    __tablename__ = "lesson_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    text_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    theme: Mapped["Theme"] = relationship(back_populates="cards")

    def localized_text(self, language: Optional[str]) -> str:
        return _loc(self.text, self.text_ru, self.text_en, language)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    text: Mapped[str] = mapped_column(Text)
    text_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options_json: Mapped[str] = mapped_column(Text)
    options_json_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options_json_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correct_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    option_images_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    theme: Mapped["Theme"] = relationship(back_populates="questions")

    @property
    def option_images(self) -> Optional[list[str]]:
        return json.loads(self.option_images_json) if self.option_images_json else None

    def localized_text(self, language: Optional[str]) -> str:
        return _loc(self.text, self.text_ru, self.text_en, language)

    def localized_options(self, language: Optional[str]) -> list[str]:
        lang = _lang(language)
        raw = self.options_json
        if lang == "ru" and self.options_json_ru:
            raw = self.options_json_ru
        elif lang == "en" and self.options_json_en:
            raw = self.options_json_en
        return json.loads(raw)

    def localized_explanation(self, language: Optional[str]) -> Optional[str]:
        return _loc(self.explanation or "", self.explanation_ru, self.explanation_en, language) or None

    @property
    def options(self) -> list[str]:
        return json.loads(self.options_json)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128))
    course_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    faculty: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    major_id: Mapped[Optional[int]] = mapped_column(ForeignKey("majors.id"), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    group_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    major: Mapped[Optional["Major"]] = relationship()


class QuizServe(Base):
    """Every question shown to a user, recorded when a quiz is generated.
    Used together with Attempt so that a student never sees a question
    again until the whole theme bank is exhausted — even if they abandoned
    the quiz without submitting."""

    __tablename__ = "quiz_serves"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    served_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class WelcomeMessage(Base):
    """The last /start message the bot sent to each chat. When the Mini App
    URL changes, the bot edits these messages in place so the "Open the app"
    button students already have keeps working."""

    __tablename__ = "welcome_messages"

    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(512), default="")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class ThemeProgress(Base):
    __tablename__ = "theme_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    lesson_read: Mapped[bool] = mapped_column(Boolean, default=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True
    )


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)


# --- Majors / profile ---------------------------------------------------------


def list_majors() -> list[dict]:
    with SessionLocal() as session:
        majors = session.scalars(select(Major)).all()
        return [
            {
                "id": m.id,
                "code": m.code,
                "name": m.name,
                "name_ru": m.name_ru,
                "name_en": m.name_en,
                "faculty": m.faculty,
                "faculty_ru": m.faculty_ru,
                "faculty_en": m.faculty_en,
            }
            for m in majors
        ]


def get_or_create_user(telegram_id: int, username: Optional[str], full_name: str) -> dict:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            user = User(telegram_id=telegram_id, username=username, full_name=full_name)
            session.add(user)
            session.commit()
            session.refresh(user)
        return _user_to_dict(user)


def update_user_profile(
    telegram_id: int,
    full_name: str,
    course_year: int,
    faculty: str,
    major_id: int,
    language: str,
    group_name: str,
) -> dict:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            raise ValueError("user not found")
        user.full_name = full_name
        user.course_year = course_year
        user.faculty = faculty
        user.major_id = major_id
        user.language = language
        user.group_name = group_name
        session.commit()
        session.refresh(user)
        return _user_to_dict(user)


def get_user(telegram_id: int) -> Optional[dict]:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.telegram_id == telegram_id))
        return _user_to_dict(user) if user else None


def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "full_name": user.full_name,
        "course_year": user.course_year,
        "faculty": user.faculty,
        "major_id": user.major_id,
        "major_name": user.major.localized_name(user.language) if user.major else None,
        "language": user.language,
        "group_name": user.group_name,
        "is_onboarded": user.course_year is not None and user.major_id is not None,
    }


# --- Subjects / themes / lessons ----------------------------------------------


def list_subjects_for_user(major_id: int, course_year: int, language: Optional[str] = None) -> list[dict]:
    with SessionLocal() as session:
        subjects = session.scalars(
            select(Subject)
            .where(Subject.major_id == major_id, Subject.course_year == course_year)
            .order_by(Subject.is_elective, Subject.order_index)
        ).all()
        result = []
        for s in subjects:
            theme_count = session.scalar(
                select(func.count()).select_from(Theme).where(Theme.subject_id == s.id)
            )
            result.append(
                {
                    "id": s.id,
                    "name": s.localized_name(language),
                    "semester": s.semester,
                    "is_elective": s.is_elective,
                    "track": s.track,
                    "theme_count": theme_count or 0,
                }
            )
        return result


def list_themes_for_subject(
    subject_id: int, user_id: Optional[int] = None, language: Optional[str] = None
) -> dict:
    with SessionLocal() as session:
        subject = session.get(Subject, subject_id)
        themes = session.scalars(
            select(Theme).where(Theme.subject_id == subject_id).order_by(Theme.order_index)
        ).all()
        result = []
        for t in themes:
            question_count = session.scalar(
                select(func.count()).select_from(Question).where(Question.theme_id == t.id)
            )
            progress = None
            if user_id:
                progress = session.scalar(
                    select(ThemeProgress).where(
                        ThemeProgress.user_id == user_id, ThemeProgress.theme_id == t.id
                    )
                )
            result.append(
                {
                    "id": t.id,
                    "title": t.localized_title(language),
                    # Bank size is deliberately not exposed to students.
                    "has_questions": bool(question_count),
                    "best_score": progress.best_score if progress else 0,
                }
            )
        return {
            "subject": (
                {"id": subject.id, "name": subject.localized_name(language)} if subject else None
            ),
            "themes": result,
        }


def get_quiz_questions(
    theme_id: int,
    limit: int = 10,
    language: Optional[str] = None,
    user_id: Optional[int] = None,
) -> list[dict]:
    """Picks `limit` questions for a quiz, never repeating for a user until
    the theme's bank is exhausted.

    Priority: (1) questions never shown to the user, random order;
    (2) shown before but never answered (abandoned quiz), oldest first;
    (3) answered wrong, least recently first; (4) answered right, least
    recently first. Every served question is recorded in quiz_serves.
    """
    with SessionLocal() as session:
        questions = list(
            session.scalars(select(Question).where(Question.theme_id == theme_id))
        )
        random.shuffle(questions)
        qids = [q.id for q in questions]

        last_attempt: dict[int, tuple[int, bool]] = {}
        last_serve: dict[int, int] = {}
        if user_id and qids:
            for qid, attempt_id, is_correct in session.execute(
                select(Attempt.question_id, Attempt.id, Attempt.is_correct)
                .where(Attempt.user_id == user_id, Attempt.question_id.in_(qids))
                .order_by(Attempt.id)
            ):
                last_attempt[qid] = (attempt_id, bool(is_correct))
            for qid, serve_id in session.execute(
                select(QuizServe.question_id, QuizServe.id)
                .where(QuizServe.user_id == user_id, QuizServe.question_id.in_(qids))
                .order_by(QuizServe.id)
            ):
                last_serve[qid] = serve_id

        def rank(q: Question) -> tuple:
            if q.id in last_attempt:
                attempt_id, correct = last_attempt[q.id]
                return (3 if correct else 2, attempt_id)
            if q.id in last_serve:
                return (1, last_serve[q.id])
            return (0, 0)  # unseen; shuffle order decides among these

        ordered = sorted(questions, key=rank)
        chosen = ordered[:limit]
        if chosen and chosen[0].id in last_attempt or chosen and chosen[0].id in last_serve:
            random.shuffle(chosen)  # mixing old ones in: don't present them sorted

        if user_id and chosen:
            session.add_all(QuizServe(user_id=user_id, question_id=q.id) for q in chosen)
            session.commit()

        return [
            {
                "id": q.id,
                "text": q.localized_text(language),
                "options": q.localized_options(language),
                "correct_index": q.correct_index,
                "explanation": q.localized_explanation(language),
                "image_url": q.image_url,
                "option_images": q.option_images,
            }
            for q in chosen
        ]


def submit_quiz(
    user_id: int, theme_id: int, answers: list[dict], language: Optional[str] = None
) -> dict:
    """answers: list of {"question_id": int, "selected_index": int}"""
    with SessionLocal() as session:
        questions = {
            q.id: q
            for q in session.scalars(
                select(Question).where(Question.theme_id == theme_id)
            )
        }
        results = []
        correct_count = 0
        for answer in answers:
            question = questions.get(answer["question_id"])
            if not question:
                continue
            is_correct = answer["selected_index"] == question.correct_index
            if is_correct:
                correct_count += 1
            session.add(
                Attempt(
                    user_id=user_id, question_id=question.id, is_correct=is_correct
                )
            )
            results.append(
                {
                    "question_id": question.id,
                    "is_correct": is_correct,
                    "correct_index": question.correct_index,
                    "explanation": question.localized_explanation(language),
                }
            )

        total = len(answers)
        score_pct = round(100 * correct_count / total) if total else 0

        progress = session.scalar(
            select(ThemeProgress).where(
                ThemeProgress.user_id == user_id, ThemeProgress.theme_id == theme_id
            )
        )
        if not progress:
            progress = ThemeProgress(
                user_id=user_id, theme_id=theme_id, best_score=0, attempts_count=0
            )
            session.add(progress)
        progress.attempts_count += 1
        progress.best_score = max(progress.best_score, score_pct)
        progress.last_attempt_at = datetime.datetime.utcnow()

        session.commit()

        return {
            "correct_count": correct_count,
            "total": total,
            "score_pct": score_pct,
            "results": results,
        }


def get_user_progress_summary(user_id: int) -> dict:
    with SessionLocal() as session:
        total_attempts = session.scalar(
            select(func.count()).select_from(Attempt).where(Attempt.user_id == user_id)
        )
        correct_attempts = session.scalar(
            select(func.count())
            .select_from(Attempt)
            .where(Attempt.user_id == user_id, Attempt.is_correct.is_(True))
        )
        themes_started = session.scalar(
            select(func.count())
            .select_from(ThemeProgress)
            .where(ThemeProgress.user_id == user_id)
        )
        themes_mastered = session.scalar(
            select(func.count())
            .select_from(ThemeProgress)
            .where(ThemeProgress.user_id == user_id, ThemeProgress.best_score >= 80)
        )
        return {
            "total_attempts": total_attempts or 0,
            "correct_attempts": correct_attempts or 0,
            "themes_started": themes_started or 0,
            "themes_mastered": themes_mastered or 0,
        }


# --- Welcome messages (Mini App URL refresh) ----------------------------------


def remember_welcome_message(chat_id: int, message_id: int, url: str) -> None:
    with SessionLocal() as session:
        row = session.get(WelcomeMessage, chat_id)
        if row is None:
            session.add(WelcomeMessage(chat_id=chat_id, message_id=message_id, url=url))
        else:
            row.message_id = message_id
            row.url = url
        session.commit()


def list_welcome_messages_needing_url(url: str) -> list[dict]:
    """Chats whose last welcome message still carries a different URL."""
    with SessionLocal() as session:
        rows = session.scalars(
            select(WelcomeMessage).where(WelcomeMessage.url != url)
        ).all()
        return [{"chat_id": r.chat_id, "message_id": r.message_id} for r in rows]


def mark_welcome_message_url(chat_id: int, url: str) -> None:
    with SessionLocal() as session:
        row = session.get(WelcomeMessage, chat_id)
        if row is not None:
            row.url = url
            session.commit()


def forget_welcome_message(chat_id: int) -> None:
    with SessionLocal() as session:
        row = session.get(WelcomeMessage, chat_id)
        if row is not None:
            session.delete(row)
            session.commit()


# --- Admin dashboard functions ------------------------------------------------


def get_admin_stats() -> dict:
    """Get overall statistics for the admin dashboard."""
    with SessionLocal() as session:
        total_users = session.scalar(select(func.count()).select_from(User)) or 0
        onboarded_users = session.scalar(
            select(func.count()).select_from(User).where(User.course_year.isnot(None))
        ) or 0
        total_attempts = session.scalar(
            select(func.count()).select_from(Attempt)
        ) or 0

        return {
            "total_users": total_users,
            "onboarded_users": onboarded_users,
            "total_attempts": total_attempts,
        }


def get_admin_users(limit: int = 100, offset: int = 0) -> list[dict]:
    """Get user list with activity stats for admin dashboard."""
    with SessionLocal() as session:
        users = session.scalars(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        ).all()

        result = []
        for user in users:
            attempts = session.scalar(
                select(func.count()).select_from(Attempt).where(Attempt.user_id == user.id)
            ) or 0
            correct = session.scalar(
                select(func.count()).select_from(Attempt).where(
                    Attempt.user_id == user.id,
                    Attempt.is_correct.is_(True)
                )
            ) or 0

            last_attempt = session.scalar(
                select(Attempt.created_at).where(Attempt.user_id == user.id)
                .order_by(Attempt.created_at.desc())
            )

            themes_started = session.scalar(
                select(func.count()).select_from(ThemeProgress).where(
                    ThemeProgress.user_id == user.id
                )
            ) or 0

            result.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "course_year": user.course_year,
                "faculty": user.faculty,
                "group_name": user.group_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "is_onboarded": user.course_year is not None,
                "attempts_count": attempts,
                "correct_count": correct,
                "accuracy": round(100 * correct / attempts) if attempts > 0 else 0,
                "themes_started": themes_started,
                "last_activity": last_attempt.isoformat() if last_attempt else None,
            })

        return result


def get_admin_user_detail(user_id: int) -> Optional[dict]:
    """Get detailed activity for a specific user."""
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            return None

        # Basic user info
        result = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "course_year": user.course_year,
            "faculty": user.faculty,
            "group_name": user.group_name,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        # Theme progress
        progresses = session.scalars(
            select(ThemeProgress).where(ThemeProgress.user_id == user_id)
        ).all()

        result["theme_progress"] = [
            {
                "theme_id": p.theme_id,
                "attempts": p.attempts_count,
                "best_score": p.best_score,
                "last_attempt": p.last_attempt_at.isoformat() if p.last_attempt_at else None,
            }
            for p in progresses
        ]

        # Overall stats
        attempts = session.scalars(
            select(Attempt).where(Attempt.user_id == user_id)
            .order_by(Attempt.created_at.desc())
        ).all()

        result["total_attempts"] = len(attempts)
        result["correct_attempts"] = sum(1 for a in attempts if a.is_correct)
        result["accuracy"] = round(100 * result["correct_attempts"] / result["total_attempts"]) if attempts else 0

        # Session info (time between first and last attempt)
        if attempts:
            first_attempt = attempts[-1].created_at
            last_attempt = attempts[0].created_at
            time_spent = (last_attempt - first_attempt).total_seconds() / 60  # minutes
            result["total_time_minutes"] = round(time_spent)
        else:
            result["total_time_minutes"] = 0

        return result


def get_admin_subject_stats() -> list[dict]:
    """Get popular subjects and themes."""
    with SessionLocal() as session:
        # Simple query: get all themes with attempts count
        from sqlalchemy import join

        themes = session.scalars(select(Theme)).all()
        result = []

        for theme in themes:
            attempts = session.scalar(
                select(func.count()).select_from(Attempt).join(
                    Question, Question.id == Attempt.question_id
                ).where(Question.theme_id == theme.id)
            ) or 0

            if attempts == 0:
                continue

            correct = session.scalar(
                select(func.count()).select_from(Attempt).join(
                    Question, Question.id == Attempt.question_id
                ).where(Question.theme_id == theme.id, Attempt.is_correct.is_(True))
            ) or 0

            subject = session.get(Subject, theme.subject_id)

            result.append({
                "theme_id": theme.id,
                "theme_name": theme.title,
                "subject_name": subject.name if subject else "Unknown",
                "attempts": attempts,
                "accuracy": round(100 * correct / attempts) if attempts > 0 else 0,
            })

        # Sort by attempts descending and limit to 50
        result.sort(key=lambda x: x["attempts"], reverse=True)
        return result[:50]
