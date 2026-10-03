"""Merges generated question files into a content/lessons_*_bank.json file
that bot/seed.py loads on startup.

    python scripts/merge_bank.py --bank DIR --base content/lessons_statistics.json \
        --out content/lessons_statistics_bank.json --subject STAT1305

Files in DIR are named tNN_X_K.json where NN is the 1-based theme index in
the base file's theme list. Validation: exactly 4 distinct options in all
three languages, correct_index in range, all texts non-empty; duplicates (by
normalized English or Uzbek text) are dropped, both within the generated
set and against the base file.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = ["text", "text_ru", "text_en", "options", "options_ru", "options_en",
            "correct_index", "explanation", "explanation_ru", "explanation_en"]


def norm(s: str) -> str:
    return re.sub(r"[\W_]+", " ", str(s).lower()).strip()


def _tidy(v):
    """Normalises the apostrophe variants (ʻ ’ ‘ ʼ) that appear in Uzbek
    Latin text (o'rtacha, ma'lumot) to the plain ASCII apostrophe."""
    if isinstance(v, str):
        return v.translate(str.maketrans({"ʻ": "'", "’": "'", "‘": "'", "ʼ": "'"}))
    if isinstance(v, list):
        return [_tidy(x) for x in v]
    return v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True, type=Path)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--subject", required=True)
    args = ap.parse_args()

    base = json.loads(args.base.read_text(encoding="utf-8"))
    entry = next(e for e in base if e["subject_code"] == args.subject)
    themes = entry["themes"]

    seen_norm = {norm(q.get("text_en") or q["text"]) for t in themes for q in t["questions"]}
    seen_uz = {q["text"] for t in themes for q in t["questions"]}

    per_theme: dict[int, list[dict]] = defaultdict(list)
    rejected: Counter = Counter()
    for path in sorted(args.bank.glob("t*_*.json")):
        idx = int(path.name[1:3])
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"SKIP {path.name}: invalid JSON ({exc})")
            continue
        for q in items:
            try:
                for k in REQUIRED:
                    if k not in q or q[k] in (None, "", []):
                        raise ValueError(f"missing {k}")
                for k in ("options", "options_ru", "options_en"):
                    if len(q[k]) != 4 or any(not str(o).strip() for o in q[k]):
                        raise ValueError(f"bad {k}")
                    if len({norm(o) for o in q[k]}) != 4:
                        raise ValueError(f"duplicate options in {k}")
                if not 0 <= int(q["correct_index"]) < 4:
                    raise ValueError("bad correct_index")
            except (ValueError, TypeError) as exc:
                rejected[str(exc)] += 1
                continue
            key = norm(q["text_en"])
            if key in seen_norm or q["text"] in seen_uz:
                rejected["duplicate"] += 1
                continue
            seen_norm.add(key)
            seen_uz.add(q["text"])
            per_theme[idx].append({k: _tidy(q[k]) for k in REQUIRED + ["source"] if k in q})

    out_themes = []
    for i, t in enumerate(themes, 1):
        qs = per_theme.get(i, [])
        out_themes.append({"title": t["title"], "title_ru": t.get("title_ru"),
                           "title_en": t.get("title_en"), "questions": qs})
        dist = Counter(q["correct_index"] for q in qs)
        print(f"theme {i:2d}: {len(qs):4d} new  spread {dict(sorted(dist.items()))}  "
              f"(base has {len(t['questions'])})")

    args.out.write_text(json.dumps([{"subject_code": args.subject, "themes": out_themes}],
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(t["questions"]) for t in out_themes)
    print(f"wrote {args.out} with {total} questions; rejected: {dict(rejected)}")


if __name__ == "__main__":
    main()
