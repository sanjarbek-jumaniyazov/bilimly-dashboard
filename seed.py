from __future__ import annotations

import json

from sqlalchemy import select

from bot.config import BASE_DIR
from bot.db import LessonCard, Major, Question, SessionLocal, Subject, Theme

CONTENT_DIR = BASE_DIR / "content"


def seed_curriculum() -> None:
    """Loads content/curriculum.json: one major + its full subject list
    (per course year / semester). Safe to re-run: existing subjects (matched
    by major + code) are left untouched.
    """
    path = CONTENT_DIR / "curriculum.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))

    with SessionLocal() as session:
        major_data = data["major"]
        major = session.scalar(select(Major).where(Major.code == major_data["code"]))
        if not major:
            major = Major(
                code=major_data["code"],
                name=major_data["name"],
                name_ru=major_data.get("name_ru"),
                name_en=major_data.get("name_en"),
                faculty=major_data["faculty"],
                faculty_ru=major_data.get("faculty_ru"),
                faculty_en=major_data.get("faculty_en"),
            )
            session.add(major)
            session.commit()
            session.refresh(major)
        else:
            major.name_ru = major_data.get("name_ru")
            major.name_en = major_data.get("name_en")
            major.faculty_ru = major_data.get("faculty_ru")
            major.faculty_en = major_data.get("faculty_en")
            session.commit()

        for order_index, subject_data in enumerate(data["subjects"]):
            existing = session.scalar(
                select(Subject).where(
                    Subject.major_id == major.id, Subject.code == subject_data["code"]
                )
            )
            if existing:
                # curriculum.json is the source of truth for subject metadata
                # (including translations), so refresh it on every restart.
                existing.course_year = subject_data["course_year"]
                existing.semester = subject_data.get("semester")
                existing.name = subject_data["name"]
                existing.name_ru = subject_data.get("name_ru")
                existing.name_en = subject_data.get("name_en")
                existing.is_elective = subject_data.get("is_elective", False)
                existing.track = subject_data.get("track")
                existing.order_index = order_index
                continue
            session.add(
                Subject(
                    major_id=major.id,
                    course_year=subject_data["course_year"],
                    semester=subject_data.get("semester"),
                    code=subject_data["code"],
                    name=subject_data["name"],
                    name_ru=subject_data.get("name_ru"),
                    name_en=subject_data.get("name_en"),
                    is_elective=subject_data.get("is_elective", False),
                    track=subject_data.get("track"),
                    order_index=order_index,
                )
            )
        session.commit()


def seed_lessons() -> None:
    """Loads content/demo_lessons.json and any content/lessons_*.json files:
    themes (with quiz questions, and legacy lesson cards if present) attached
    to subjects by code. Safe to re-run: existing questions (matched by text)
    are left untouched, and new ones in the JSON are added to the pool.

    Supports two formats:
    1. Old: array of {subject_code, themes}
    2. New: {subject: {code, ...}, chapters}
    """
    paths = [CONTENT_DIR / "demo_lessons.json", *sorted(CONTENT_DIR.glob("lessons_*.json"))]

    with SessionLocal() as session:
        for path in paths:
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))

            # Detect format: new has "subject" key at top level, old is an array
            if isinstance(data, dict) and "subject" in data and "chapters" in data:
                # New format: {subject, chapters}
                subject_code = data["subject"]["code"]
                subject = session.scalar(select(Subject).where(Subject.code == subject_code))
                if not subject:
                    continue

                for order_index, chapter in enumerate(data["chapters"]):
                    theme_number = chapter["number"]
                    theme_title = chapter["title_en"]  # Use English title as primary

                    theme = session.scalar(
                        select(Theme).where(
                            Theme.subject_id == subject.id,
                            Theme.order_index == theme_number - 1,
                        )
                    )
                    if not theme:
                        theme = Theme(
                            subject_id=subject.id,
                            title=chapter.get("title_uz", theme_title),
                            title_ru=chapter.get("title_ru"),
                            title_en=theme_title,
                            order_index=theme_number - 1,
                        )
                        session.add(theme)
                        session.commit()
                        session.refresh(theme)

                    # Add questions for this chapter
                    existing_by_text = {
                        row.text_en: row
                        for row in session.scalars(
                            select(Question).where(Question.theme_id == theme.id)
                        )
                    }

                    for q in chapter.get("questions", []):
                        # Match by English text since Uzbek/Russian stems may not be in JSON
                        existing_q = existing_by_text.get(q.get("text_en"))
                        if existing_q is not None:
                            existing_q.options_json = json.dumps(q["options"], ensure_ascii=False)
                            existing_q.options_json_ru = (
                                json.dumps(q["options_ru"], ensure_ascii=False)
                                if q.get("options_ru") else None
                            )
                            existing_q.options_json_en = (
                                json.dumps(q["options_en"], ensure_ascii=False)
                                if q.get("options_en") else None
                            )
                            existing_q.correct_index = q["correct_index"]
                            existing_q.text_en = q.get("text_en")
                            existing_q.explanation_en = q.get("explanation_en")
                            continue

                        session.add(
                            Question(
                                theme_id=theme.id,
                                text=q.get("text_en", ""),
                                text_en=q.get("text_en"),
                                options_json=json.dumps(q["options"], ensure_ascii=False),
                                options_json_en=(
                                    json.dumps(q["options_en"], ensure_ascii=False)
                                    if q.get("options_en") else None
                                ),
                                options_json_ru=(
                                    json.dumps(q["options_ru"], ensure_ascii=False)
                                    if q.get("options_ru") else None
                                ),
                                correct_index=q["correct_index"],
                                explanation_en=q.get("explanation_en"),
                            )
                        )
                    session.commit()
            else:
                # Old format: array of entries
                entries = data if isinstance(data, list) else []
                for entry in entries:
                    subject = session.scalar(
                        select(Subject).where(Subject.code == entry["subject_code"])
                    )
                    if not subject:
                        continue

                    for order_index, theme_data in enumerate(entry["themes"]):
                        theme = session.scalar(
                            select(Theme).where(
                                Theme.subject_id == subject.id,
                                Theme.title == theme_data["title"],
                            )
                        )
                        if not theme:
                            theme = Theme(
                                subject_id=subject.id,
                                title=theme_data["title"],
                                title_ru=theme_data.get("title_ru"),
                                title_en=theme_data.get("title_en"),
                                order_index=order_index,
                            )
                            session.add(theme)
                            session.commit()
                            session.refresh(theme)
                        else:
                            theme.title_ru = theme_data.get("title_ru")
                            theme.title_en = theme_data.get("title_en")
                            theme.order_index = order_index

                        existing_cards = session.scalar(
                            select(LessonCard).where(LessonCard.theme_id == theme.id)
                        )
                        if not existing_cards:
                            for card_index, card in enumerate(theme_data.get("cards", [])):
                                # a card is either a plain string (uz only) or an
                                # {"uz": ..., "ru": ..., "en": ...} object.
                                if isinstance(card, str):
                                    card = {"uz": card}
                                session.add(
                                    LessonCard(
                                        theme_id=theme.id,
                                        order_index=card_index,
                                        text=card["uz"],
                                        text_ru=card.get("ru"),
                                        text_en=card.get("en"),
                                    )
                                )

                        # Add only questions that aren't already in the DB (matched
                        # by text), so re-running seed after adding new questions
                        # to the JSON grows the bank instead of being skipped.
                        existing_by_text = {
                            row.text: row
                            for row in session.scalars(
                                select(Question).where(Question.theme_id == theme.id)
                            )
                        }
                        for q in theme_data.get("questions", []):
                            existing_q = existing_by_text.get(q["text"])
                            if existing_q is not None:
                                # The JSON is the source of truth: refresh options,
                                # answer and explanations so content fixes (e.g.
                                # rebalanced option lengths) reach the live app
                                # without losing the question id / attempt history.
                                existing_q.options_json = json.dumps(q["options"], ensure_ascii=False)
                                existing_q.options_json_ru = (
                                    json.dumps(q["options_ru"], ensure_ascii=False)
                                    if q.get("options_ru") else None
                                )
                                existing_q.options_json_en = (
                                    json.dumps(q["options_en"], ensure_ascii=False)
                                    if q.get("options_en") else None
                                )
                                existing_q.correct_index = q["correct_index"]
                                existing_q.text_ru = q.get("text_ru")
                                existing_q.text_en = q.get("text_en")
                                existing_q.explanation = q.get("explanation")
                                existing_q.explanation_ru = q.get("explanation_ru")
                                existing_q.explanation_en = q.get("explanation_en")
                                continue
                            options_ru = q.get("options_ru")
                            options_en = q.get("options_en")
                            option_images = q.get("option_images")
                            session.add(
                                Question(
                                    theme_id=theme.id,
                                    text=q["text"],
                                    text_ru=q.get("text_ru"),
                                    text_en=q.get("text_en"),
                                    options_json=json.dumps(q["options"], ensure_ascii=False),
                                    options_json_ru=(
                                        json.dumps(options_ru, ensure_ascii=False)
                                        if options_ru
                                        else None
                                    ),
                                    options_json_en=(
                                        json.dumps(options_en, ensure_ascii=False)
                                        if options_en
                                        else None
                                    ),
                                    correct_index=q["correct_index"],
                                    explanation=q.get("explanation"),
                                    explanation_ru=q.get("explanation_ru"),
                                    explanation_en=q.get("explanation_en"),
                                    image_url=q.get("image_url"),
                                    option_images_json=(
                                        json.dumps(option_images, ensure_ascii=False)
                                        if option_images
                                        else None
                                    ),
                                )
                            )
                        session.commit()


def seed_all() -> None:
    seed_curriculum()
    seed_lessons()
