"""Turn raw teacher material (lecture notes, slides exported to text, textbook
excerpts) into a lesson file (short reading cards + a quiz) that bot/seed.py
loads into the database for a given subject/theme.

Usage:
    python scripts/generate_quiz.py \
        --input materials/week3_grammar.txt \
        --subject-code XT11210 \
        --theme "Week 3: Reported Speech" \
        --num-questions 8 \
        --output content/lessons_week3.json

Requires ANTHROPIC_API_KEY to be set (see .env.example). --subject-code must
match a "code" already present in content/curriculum.json. The generated file
still needs a quick human read-through before it goes live — the pipeline
produces a first draft, not a published lesson.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from anthropic import Anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.config import ANTHROPIC_API_KEY  # noqa: E402

SYSTEM_PROMPT = """You are an assistant that turns university study material \
into a short, Khan-Academy-style lesson for exam prep, based only on the \
material given to you.

Produce two things:
1. "cards": 3-6 short reading cards (2-4 sentences each) that explain the key \
   concepts in the material, in a logical learning order. Plain, clear \
   language a student can read in under a minute per card. No fluff, no \
   restating the obvious.
2. "questions": multiple-choice questions that test real understanding of \
   those cards (not just word-matching). Each has exactly 4 options with \
   exactly one correct answer, plus a one-sentence explanation of why that \
   answer is correct.

Match the language of the input material (if the material is in Uzbek, write \
the lesson in Uzbek; if English, write it in English; if Russian, in \
Russian).

Respond with ONLY a JSON object (no prose, no markdown fences) in this exact \
shape:
{
  "cards": ["card 1 text", "card 2 text", "..."],
  "questions": [
    {
      "text": "question text",
      "options": ["option A", "option B", "option C", "option D"],
      "correct_index": 0,
      "explanation": "why this answer is correct"
    }
  ]
}
"""


def generate_lesson(material: str, num_questions: int, model: str) -> dict:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and paste "
            "your key from console.anthropic.com."
        )

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate a lesson with {num_questions} quiz questions "
                    f"from this study material:\n\n{material}"
                ),
            }
        ],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    return json.loads(raw_text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to a .txt file with the material")
    parser.add_argument(
        "--subject-code", required=True, help="Subject code from content/curriculum.json"
    )
    parser.add_argument("--theme", required=True, help="e.g. 'Week 3: Reported Speech'")
    parser.add_argument("--num-questions", type=int, default=6)
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--output", required=True, help="Where to write the lesson JSON")
    args = parser.parse_args()

    material = Path(args.input).read_text(encoding="utf-8")
    lesson = generate_lesson(material, args.num_questions, args.model)

    output_data = [
        {
            "subject_code": args.subject_code,
            "themes": [
                {
                    "title": args.theme,
                    "cards": lesson["cards"],
                    "questions": lesson["questions"],
                }
            ],
        }
    ]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Wrote {len(lesson['cards'])} cards and {len(lesson['questions'])} "
        f"questions to {output_path}"
    )
    print(
        "Review the lesson before running the bot — seed.py auto-loads any "
        "content/lessons_*.json file on startup."
    )


if __name__ == "__main__":
    main()
