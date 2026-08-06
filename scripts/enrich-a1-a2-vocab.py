#!/usr/bin/env python3
"""
Enrich A1–A2 lesson JSON with full DaF kompakt vocabulary.

Sources:
  1) Anki deck Daf_kompakt_A1-B1_Deutsch_to_Persisch.apkg (lemma + article)
  2) Front Back.txt / DafKompact A1 Verben.txt (DE→EN verbs)
  3) Existing lesson JSON English
  4) OCR page text from DaF-kompakt-A1-B1-KB-ocr.pdf (lesson assignment)
  5) GoogleTranslator for remaining English glosses (cached)
"""
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

# TOC start pages (1-based); end exclusive via next start
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
}
NEXT_START = 156  # B1 L19


def lesson_id(n: int) -> str:
    return f"{'a1' if n <= 8 else 'a2'}-l{n:02d}"


def load_en_cache() -> dict[str, str]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def save_en_cache(cache: dict[str, str]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def parse_front_back() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ["Front   Back.txt", "DafKompact A1 Verben.txt", "DW list.txt"]:
        p = ROOT / name
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8-sig", errors="ignore")
        # CR line endings
        for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            if "\t" not in line:
                continue
            front, back = line.split("\t", 1)
            de = re.sub(r"\s*\((DaF|DW)\).*$", "", front).strip()
            de = re.sub(r"\s*\[Verb\]\s*$", "", de).strip()
            # English is usually before first " / "
            en = back.split(" / ")[0].strip()
            en = re.sub(r"^to\s+", "to ", en)
            if de and en:
                out[de.lower()] = en
    return out


def parse_anki(tmp_dir: Path) -> list[dict]:
    with zipfile.ZipFile(ANKI) as z:
        z.extract("collection.anki2", tmp_dir)
    con = sqlite3.connect(tmp_dir / "collection.anki2")
    cur = con.cursor()
    items = []
    for (flds,) in cur.execute("select flds from notes"):
        parts = flds.split("\x1f")
        front = (parts[0] or "").strip()
        back = (parts[1] or "").strip() if len(parts) > 1 else ""
        if not front or len(front) > 60:
            continue
        # skip junk
        if re.search(r"[ا-ی]", front):
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
        # verb heuristic
        if front.endswith("en") or front.endswith("eln") or front.endswith("ern"):
            if not article:
                pos = "verb"
        if " " in front and not front[0].isupper():
            pos = "phrase"
        # clean lemma
        de = front.replace("\u00ad", "").strip()
        if not re.match(r"^[A-Za-zÄÖÜäöüß\- ]+$", de):
            continue
        items.append({"de": de, "article": article, "pos": pos})
    con.close()
    # dedupe by lower de, prefer with article
    by = {}
    for it in items:
        k = it["de"].lower()
        if k not in by or (it["article"] and not by[k]["article"]):
            by[k] = it
    return list(by.values())


def normalize_ocr(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_german(text: str) -> set[str]:
    words = re.findall(r"[A-Za-zÄÖÜäöüß]{2,}", text)
    return {w.lower() for w in words}


def translate_missing(words: list[str], cache: dict[str, str]) -> dict[str, str]:
    from deep_translator import GoogleTranslator

    t = GoogleTranslator(source="de", target="en")
    missing = [w for w in words if w.lower() not in cache]
    print(f"Translating {len(missing)} glosses in batches…", flush=True)
    batch_size = 25
    for i in range(0, len(missing), batch_size):
        batch = missing[i : i + batch_size]
        try:
            ens = t.translate_batch(batch)
            for w, en in zip(batch, ens):
                cache[w.lower()] = en if isinstance(en, str) and en else w
        except Exception as e:
            print(f"batch fail at {i}: {e} — falling back one-by-one", flush=True)
            for w in batch:
                try:
                    cache[w.lower()] = t.translate(w)
                    time.sleep(0.08)
                except Exception as e2:
                    print("fail", w, e2, flush=True)
                    cache[w.lower()] = w
                    time.sleep(1.0)
        save_en_cache(cache)
        print(f"  {min(i + batch_size, len(missing))}/{len(missing)}", flush=True)
        time.sleep(0.35)
    save_en_cache(cache)
    return cache


def build_vocab_entry(de: str, article, pos, en: str, idx: int) -> dict:
    entry = {
        "id": f"v{idx}",
        "de": de,
        "en": en,
        "pos": pos if pos in {"noun", "verb", "adjective", "adverb", "phrase", "other"} else "other",
    }
    if article in {"der", "die", "das"}:
        entry["article"] = article
        entry["pos"] = "noun"
    return entry


def main() -> None:
    print("Loading sources…")
    en_maps = parse_front_back()
    cache = load_en_cache()
    # seed cache from front-back
    for k, v in en_maps.items():
        cache.setdefault(k, v)

    tmp = Path("/tmp/anki-daf-enrich")
    tmp.mkdir(exist_ok=True)
    anki = parse_anki(tmp)
    print(f"Anki unique lemmas: {len(anki)}")

    # existing lesson EN
    existing_by_lesson: dict[int, dict[str, dict]] = {}
    for n in range(1, 19):
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        m = {}
        for v in data.get("vocab", []):
            m[v["de"].lower()] = v
        existing_by_lesson[n] = m
        for v in data.get("vocab", []):
            cache.setdefault(v["de"].lower(), v["en"])

    print("Reading PDF…")
    reader = PdfReader(str(PDF))
    starts = LESSON_STARTS
    ordered = sorted(starts.keys())

    # Prebuild anki lookup
    anki_by_lower = {a["de"].lower(): a for a in anki}
    # also multiword phrases
    phrase_ankis = [a for a in anki if " " in a["de"]]

    lesson_lemmas: dict[int, dict[str, dict]] = {n: {} for n in ordered}

    for n in ordered:
        start = starts[n]
        end = starts[n + 1] - 1 if n + 1 in starts else NEXT_START - 1
        texts = []
        for p in range(start, end + 1):
            texts.append(reader.pages[p - 1].extract_text() or "")
        blob = normalize_ocr("\n".join(texts))
        tokens = tokenize_german(blob)
        print(f"L{n:02d} pages {start}-{end}: {len(tokens)} OCR tokens")

        # match single-token anki lemmas
        for tok in tokens:
            if tok in anki_by_lower:
                lesson_lemmas[n][tok] = anki_by_lower[tok]

        # match multiword phrases if present in blob lower
        blob_l = blob.lower()
        for a in phrase_ankis:
            key = a["de"].lower()
            if key in blob_l:
                lesson_lemmas[n][key] = a

        # keep all existing lesson vocab too
        for k, v in existing_by_lesson[n].items():
            if k not in lesson_lemmas[n]:
                lesson_lemmas[n][k] = {
                    "de": v["de"],
                    "article": v.get("article"),
                    "pos": v.get("pos") or "other",
                }

    # Collect all words needing EN
    need = set()
    for n in ordered:
        for k, meta in lesson_lemmas[n].items():
            if k not in cache:
                need.add(meta["de"])
    translate_missing(sorted(need), cache)

    # Write lessons
    index_path = APP / "public" / "content" / "index.json"
    index = json.loads(index_path.read_text())

    for n in ordered:
        path = CONTENT / f"{lesson_id(n)}.json"
        data = json.loads(path.read_text())
        items = []
        # stable sort: nouns with article first, then alpha
        metas = list(lesson_lemmas[n].values())
        metas.sort(
            key=lambda m: (
                0 if m.get("article") else 1,
                0 if m.get("pos") == "verb" else 1,
                m["de"].lower(),
            )
        )
        seen = set()
        for meta in metas:
            key = meta["de"].lower()
            if key in seen:
                continue
            seen.add(key)
            prev = existing_by_lesson[n].get(key, {})
            en = prev.get("en") or cache.get(key) or meta["de"]
            # clean translator noise
            if isinstance(en, str) and en.lower().startswith("the ") and meta.get("article"):
                en = en[4:]
            entry = build_vocab_entry(
                prev.get("de") or meta["de"],
                prev.get("article") or meta.get("article"),
                prev.get("pos") or meta.get("pos") or "other",
                en,
                len(items) + 1,
            )
            if prev.get("exampleDe"):
                entry["exampleDe"] = prev["exampleDe"]
            if prev.get("exampleEn"):
                entry["exampleEn"] = prev["exampleEn"]
            items.append(entry)

        data["vocab"] = items
        data["status"] = "complete"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {path.name}: {len(items)} vocab")

        for e in index["lessons"]:
            if e["id"] == lesson_id(n):
                e["status"] = "complete"

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    save_en_cache(cache)
    print("Done.")


if __name__ == "__main__":
    main()
