#!/usr/bin/env python3
"""Enrich B1 L19–L30 lesson JSON vocab from Anki ∩ Kursbuch OCR pages."""
from __future__ import annotations

import json
import re
import sqlite3
import time
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt")
APP = ROOT / "daf-kompakt-app"
CONTENT = APP / "public" / "content" / "lektionen"
CACHE = APP / "scripts" / ".en-cache.json"
ANKI = ROOT / "Daf_kompakt_A1-B1_Deutsch_to_Persisch.apkg"
PDF = ROOT / "DaF-kompakt-A1-B1-KB-ocr.pdf"

# OCR 1-based page starts (exclusive end = next start)
LESSON_STARTS = {
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


def lesson_id(n: int) -> str:
    return f"b1-l{n:02d}"


def load_en_cache() -> dict[str, str]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def save_en_cache(cache: dict[str, str]) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def parse_anki(tmp_dir: Path) -> list[dict]:
    with zipfile.ZipFile(ANKI) as z:
        z.extract("collection.anki2", tmp_dir)
    con = sqlite3.connect(tmp_dir / "collection.anki2")
    items = []
    for (flds,) in con.execute("select flds from notes"):
        parts = flds.split("\x1f")
        front = (parts[0] or "").strip()
        back = (parts[1] or "").strip() if len(parts) > 1 else ""
        if not front or len(front) > 60 or re.search(r"[ا-ی]", front):
            continue
        article = None
        pos = "other"
        m = re.match(r"^\s*(der|die|das)\b[, ]*", back, re.I)
        if m:
            article = m.group(1).lower()
            pos = "noun"
        elif re.search(r"\b(der|die|das)\b", back[:30], re.I):
            m2 = re.search(r"\b(der|die|das)\b", back[:30], re.I)
            article = m2.group(1).lower()
            pos = "noun"
        if (front.endswith(("en", "eln", "ern"))) and not article:
            pos = "verb"
        if " " in front and not front[0].isupper():
            pos = "phrase"
        de = front.replace("\u00ad", "").strip()
        if not re.match(r"^[A-Za-zÄÖÜäöüß\- ]+$", de):
            continue
        items.append({"de": de, "article": article, "pos": pos})
    con.close()
    by: dict[str, dict] = {}
    for it in items:
        k = it["de"].lower()
        if k not in by or (it["article"] and not by[k]["article"]):
            by[k] = it
    return list(by.values())


def normalize_ocr(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u00ad", ""))


def tokenize_german(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-zÄÖÜäöüß]{2,}", text)}


def translate_missing(words: list[str], cache: dict[str, str]) -> None:
    from deep_translator import GoogleTranslator

    t = GoogleTranslator(source="de", target="en")
    missing = [w for w in words if w.lower() not in cache]
    print(f"Translating {len(missing)} glosses…", flush=True)
    for i in range(0, len(missing), 25):
        batch = missing[i : i + 25]
        try:
            ens = t.translate_batch(batch)
            for w, en in zip(batch, ens):
                cache[w.lower()] = en if isinstance(en, str) and en else w
        except Exception as e:
            print(f"batch fail: {e}", flush=True)
            for w in batch:
                try:
                    cache[w.lower()] = t.translate(w)
                    time.sleep(0.1)
                except Exception:
                    cache[w.lower()] = w
                    time.sleep(1.0)
        save_en_cache(cache)
        print(f"  {min(i + 25, len(missing))}/{len(missing)}", flush=True)
        time.sleep(0.35)


def build_vocab_entry(de: str, article, pos, en: str, idx: int, prev: dict) -> dict:
    entry = {
        "id": f"v{idx}",
        "de": de,
        "en": en,
        "pos": pos if pos in {"noun", "verb", "adjective", "adverb", "phrase", "other"} else "other",
    }
    if article in {"der", "die", "das"}:
        entry["article"] = article
        entry["pos"] = "noun"
    for k in ("fa", "audioUrl", "exampleDe", "exampleEn", "exampleFa"):
        if prev.get(k):
            entry[k] = prev[k]
    return entry


def main() -> None:
    print("Loading Anki + PDF…")
    cache = load_en_cache()
    tmp = Path("/tmp/anki-daf-b1")
    tmp.mkdir(exist_ok=True)
    anki = parse_anki(tmp)
    anki_by = {a["de"].lower(): a for a in anki}
    phrases = [a for a in anki if " " in a["de"]]
    print(f"Anki lemmas: {len(anki)}")

    reader = PdfReader(str(PDF))
    ordered = sorted(LESSON_STARTS)
    lesson_lemmas: dict[int, dict[str, dict]] = {n: {} for n in ordered}
    existing: dict[int, dict[str, dict]] = {}

    for n in ordered:
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        existing[n] = {v["de"].lower(): v for v in data.get("vocab") or []}
        for v in data.get("vocab") or []:
            cache.setdefault(v["de"].lower(), v["en"])

        start = LESSON_STARTS[n]
        end = LESSON_STARTS[n + 1] - 1 if n + 1 in LESSON_STARTS else NEXT_START - 1
        blob = normalize_ocr(
            "\n".join(reader.pages[p - 1].extract_text() or "" for p in range(start, end + 1))
        )
        tokens = tokenize_german(blob)
        print(f"L{n} pages {start}-{end}: {len(tokens)} tokens")

        for tok in tokens:
            if tok in anki_by:
                lesson_lemmas[n][tok] = anki_by[tok]
        blob_l = blob.lower()
        for a in phrases:
            key = a["de"].lower()
            if key in blob_l:
                lesson_lemmas[n][key] = a
        for k, v in existing[n].items():
            lesson_lemmas[n].setdefault(
                k,
                {"de": v["de"], "article": v.get("article"), "pos": v.get("pos") or "other"},
            )

    need = []
    for n in ordered:
        for meta in lesson_lemmas[n].values():
            if meta["de"].lower() not in cache:
                need.append(meta["de"])
    if need:
        translate_missing(sorted(set(need)), cache)

    index_path = APP / "public" / "content" / "index.json"
    index = json.loads(index_path.read_text())

    for n in ordered:
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        metas = list(lesson_lemmas[n].values())
        metas.sort(
            key=lambda m: (
                0 if m.get("article") else 1,
                0 if m.get("pos") == "verb" else 1,
                m["de"].lower(),
            )
        )
        items = []
        seen: set[str] = set()
        for meta in metas:
            key = meta["de"].lower()
            if key in seen:
                continue
            seen.add(key)
            prev = existing[n].get(key, {})
            en = prev.get("en") or cache.get(key) or meta["de"]
            if isinstance(en, str) and en.lower().startswith("the ") and meta.get("article"):
                en = en[4:]
            items.append(
                build_vocab_entry(
                    prev.get("de") or meta["de"],
                    prev.get("article") or meta.get("article"),
                    prev.get("pos") or meta.get("pos") or "other",
                    en,
                    len(items) + 1,
                    prev,
                )
            )
        data["vocab"] = items
        # keep stub until grammar generator marks complete (except L19 already complete)
        if data.get("status") != "complete" and data.get("grammar"):
            data["status"] = "complete"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {path.name}: {len(items)} vocab")

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    save_en_cache(cache)
    print("Done vocab enrich.")


if __name__ == "__main__":
    main()
