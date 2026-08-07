#!/usr/bin/env python3
"""Deduplicate vocab across lessons.

Strategy:
  - Drop textbook-meta lemmas and lemmas that appear in many lessons (chrome).
  - Assign remaining lemmas to the single lesson where they occur most often in OCR
    (tie → earliest lesson). So thematic words stay with their densest lesson.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
CONTENT = ROOT / "public" / "content" / "lektionen"
INDEX = ROOT / "public" / "content" / "index.json"
PDF = PARENT / "DaF-kompakt-A1-B1-KB-ocr.pdf"

# 1-based OCR starts (from enrich scripts)
LESSON_STARTS = {
    1: 10,
    2: 20,
    3: 28,
    4: 36,
    5: 44,
    6: 52,
    7: 60,
    8: 68,
    9: 76,
    10: 84,
    11: 92,
    12: 100,
    13: 108,
    14: 116,
    15: 124,
    16: 132,
    17: 140,
    18: 148,
    19: 157,
    20: 163,
    21: 171,
    22: 179,
    23: 187,
    24: 195,
    25: 203,
    26: 211,
    27: 221,
    28: 227,
    29: 235,
    30: 243,
}
NEXT_START = 251

META_BLOCKLIST = {
    "grammatik",
    "kursbuch",
    "übungsbuch",
    "ubungsbuch",
    "redemittel",
    "lektionswortschatz",
    "wortschatz",
    "nomen",
    "verb",
    "adjektiv",
    "adverb",
    "artikel",
    "tabelle",
    "lösung",
    "lösungen",
    "aufgabe",
    "aufgaben",
    "übung",
    "übungen",
    "ubung",
    "ubungen",
    "ergänzen",
    "erganzen",
    "markieren",
    "ankreuzen",
    "beispiel",
    "beispiele",
    "seite",
    "doppelseite",
    "kapitel",
    "gmbh",
    "partner",
    "partnerin",
    "partnerarbeit",
    "kurs",
    "hören",
    "lesen",
    "schreiben",
    "sprechen",
    "verstehen",
    "ergänzung",
    "regel",
    "regeln",
    "blick",
    "überblick",
}

# If a lemma appears in this many lessons' vocab lists, treat as chrome
MAX_LESSON_SPREAD = 8


def lesson_id(n: int) -> str:
    if n <= 8:
        return f"a1-l{n:02d}"
    if n <= 18:
        return f"a2-l{n:02d}"
    return f"b1-l{n:02d}"


def lemma_key(de: str) -> str:
    return de.replace("\u00ad", "").strip().lower()


def fix_quiz(quiz: list, vocab: list) -> None:
    by_id = {v["id"]: v for v in vocab}
    by_en = {(v.get("en") or "").lower().strip(): v for v in vocab}
    by_de = {}
    for v in vocab:
        full = f"{v['article']} {v['de']}" if v.get("article") else v["de"]
        by_de[full.lower()] = v
        by_de[v["de"].lower()] = v
    for q in quiz:
        vid = q.get("vocabId")
        if not vid:
            continue
        if vid in by_id:
            continue
        hit = None
        if q.get("type") == "vocab-de-en":
            hit = by_en.get((q.get("answer") or "").lower().strip())
        elif q.get("type") == "vocab-en-de":
            hit = by_de.get((q.get("answer") or "").lower().strip())
        if hit:
            q["vocabId"] = hit["id"]
        else:
            q.pop("vocabId", None)


def build_ocr_counts() -> dict[int, dict[str, int]]:
    """lesson_number -> {token: count}."""
    reader = PdfReader(str(PDF))
    out: dict[int, dict[str, int]] = {}
    ordered = sorted(LESSON_STARTS)
    for n in ordered:
        start = LESSON_STARTS[n]
        end = LESSON_STARTS[n + 1] - 1 if n + 1 in LESSON_STARTS else NEXT_START - 1
        text = "\n".join(
            (reader.pages[p - 1].extract_text() or "") for p in range(start, end + 1)
        )
        text = text.replace("\u00ad", "")
        counts: dict[str, int] = defaultdict(int)
        for w in re.findall(r"[A-Za-zÄÖÜäöüß]{2,}", text):
            counts[w.lower()] += 1
        out[n] = counts
        print(f"OCR L{n}: pages {start}-{end}, tokens {sum(counts.values())}")
    return out


def main() -> None:
    print("Building OCR frequency maps…")
    ocr = build_ocr_counts()

    # Load all vocab
    by_lesson: dict[int, list[dict]] = {}
    spread: dict[str, list[int]] = defaultdict(list)
    for n in sorted(LESSON_STARTS):
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        items = data.get("vocab") or []
        by_lesson[n] = items
        seen = set()
        for v in items:
            k = lemma_key(v.get("de") or "")
            if not k or k in seen:
                continue
            seen.add(k)
            spread[k].append(n)

    # Decide owner lesson for each lemma
    owners: dict[str, int] = {}
    dropped_meta = 0
    dropped_spread = 0
    for k, lessons in spread.items():
        if k in META_BLOCKLIST:
            dropped_meta += 1
            continue
        if len(lessons) >= MAX_LESSON_SPREAD:
            dropped_spread += 1
            continue
        # score by OCR count in each candidate lesson
        best_n = None
        best_score = -1
        for n in lessons:
            # prefer multi-word: count phrase roughly via first token
            tok = k.split()[0]
            score = ocr.get(n, {}).get(tok, 0)
            # slight bonus if lemma appears only here
            if len(lessons) == 1:
                score += 1000
            if score > best_score or (score == best_score and (best_n is None or n < best_n)):
                best_score = score
                best_n = n
        if best_n is not None:
            owners[k] = best_n

    kept_total = 0
    for n in sorted(LESSON_STARTS):
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        old = data.get("vocab") or []
        kept = []
        seen = set()
        for v in old:
            k = lemma_key(v.get("de") or "")
            if not k or k in seen:
                continue
            seen.add(k)
            if owners.get(k) != n:
                continue
            kept.append(v)
        for i, v in enumerate(kept, 1):
            v["id"] = f"v{i}"
        data["vocab"] = kept
        fix_quiz(data.get("quiz") or [], kept)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        kept_total += len(kept)
        print(f"{lesson_id(n)}: {len(old)} → {len(kept)}")

    print(
        f"Done. kept={kept_total} unique_owned={len(owners)} "
        f"dropped_meta={dropped_meta} dropped_spread={dropped_spread}"
    )


if __name__ == "__main__":
    main()
