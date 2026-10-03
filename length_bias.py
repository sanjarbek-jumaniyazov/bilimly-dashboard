"""Finds and fixes the "correct answer is the longest option" giveaway.

    python scripts/length_bias.py report
    python scripts/length_bias.py extract OUT_DIR [--chunk 150]
        -> OUT_DIR/chunk_NN.json, each a list of {id, text_en, options, options_ru,
           options_en, correct_index, explanation_en}; an agent rewrites the three
           option lists so all four choices are similar in length and writes
           OUT_DIR/chunk_NN.out.json with the same ids.
    python scripts/length_bias.py apply OUT_DIR
        -> writes the rewritten options back into content/*.json (matched by id).

A question is flagged when, in English, the correct option is the single
longest one and more than 10% longer than the next longest, or the single
shortest one and more than 10% shorter than the next shortest.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted((ROOT / "content").glob("lessons_*.json")) + [ROOT / "content" / "demo_lessons.json"]


def biased(q: dict) -> bool:
    opts = q.get("options_en") or q["options"]
    L = [len(o) for o in opts]
    ci = q["correct_index"]
    c = L[ci]
    others = L[:ci] + L[ci + 1:]
    if c > max(others) * 1.10:
        return True
    if c < min(others) * 0.90:
        return True
    return False


def iter_questions():
    for f in FILES:
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for si, s in enumerate(data):
            for ti, t in enumerate(s["themes"]):
                for qi, q in enumerate(t["questions"]):
                    yield f, data, f"{f.name}|{si}|{ti}|{qi}", q


def cmd_report():
    tot = flagged = longest = 0
    for _, _, _, q in iter_questions():
        tot += 1
        opts = q.get("options_en") or q["options"]
        if len(opts[q["correct_index"]]) == max(len(o) for o in opts):
            longest += 1
        if biased(q):
            flagged += 1
    print(f"{tot} questions; correct is longest in {longest} ({100*longest//tot}%); flagged {flagged} ({100*flagged//tot}%)")


def cmd_extract(out_dir: Path, chunk: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for _, _, qid, q in iter_questions():
        if biased(q):
            items.append({
                "id": qid, "text_en": q.get("text_en") or q["text"],
                "options": q["options"], "options_ru": q.get("options_ru") or q["options"],
                "options_en": q.get("options_en") or q["options"],
                "correct_index": q["correct_index"], "explanation_en": q.get("explanation_en") or q.get("explanation") or "",
            })
    for n, start in enumerate(range(0, len(items), chunk), 1):
        (out_dir / f"chunk_{n:02d}.json").write_text(
            json.dumps(items[start:start + chunk], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} flagged questions -> {n} chunks in {out_dir}")


def cmd_apply(out_dir: Path):
    fixes = {}
    for f in sorted(out_dir.glob("chunk_*.out.json")):
        try:
            for item in json.loads(f.read_text(encoding="utf-8")):
                fixes[item["id"]] = item
        except json.JSONDecodeError as exc:
            print(f"SKIP {f.name}: {exc}")
    applied = rejected = still = 0
    touched = {}
    for f, data, qid, q in iter_questions():
        fix = fixes.get(qid)
        if not fix:
            continue
        ok = True
        for k in ("options", "options_ru", "options_en"):
            v = fix.get(k)
            if not (isinstance(v, list) and len(v) == 4 and all(isinstance(o, str) and o.strip() for o in v)
                    and len({o.strip().lower() for o in v}) == 4):
                ok = False
        ci = fix.get("correct_index", q["correct_index"])
        if not (isinstance(ci, int) and 0 <= ci < 4):
            ok = False
        if not ok:
            rejected += 1
            continue
        q["options"], q["options_ru"], q["options_en"] = fix["options"], fix["options_ru"], fix["options_en"]
        q["correct_index"] = ci
        applied += 1
        if biased(q):
            still += 1
        touched[f] = data
    for f, data in touched.items():
        f.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"applied {applied}, rejected {rejected}, still biased after rewrite {still}; files updated: {len(touched)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["report", "extract", "apply"])
    ap.add_argument("out_dir", nargs="?", type=Path)
    ap.add_argument("--chunk", type=int, default=150)
    a = ap.parse_args()
    if a.cmd == "report":
        cmd_report()
    elif a.cmd == "extract":
        cmd_extract(a.out_dir, a.chunk)
    else:
        cmd_apply(a.out_dir)
