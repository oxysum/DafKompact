#!/usr/bin/env python3
"""
Enrich vocab exampleDe / exampleEn / exampleFa from listening transcripts.

Preference order:
  1. Same lesson's tracks — shortest clean sentence containing the lemma
  2. Other lessons' tracks
  3. Leave empty if nothing found

Uses normalized DE text; maps EN/FA by sentence-index when possible,
otherwise translates the German example.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
LISTEN = APP / "public" / "content" / "listening"
LESSONS = APP / "public" / "content" / "lektionen"

SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
SPEAKER_PREFIX = re.compile(r"^[^:\n]{1,48}:\s*")
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+", re.UNICODE)

# Skip meta / very short / too long examples
MIN_LEN = 12
MAX_LEN = 160


@dataclass
class Sentence:
    de: str
    en: str
    fa: str
    lesson: int
    track: str


def strip_speaker(s: str) -> str:
    return SPEAKER_PREFIX.sub("", s).strip()


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts: list[str] = []
    for turn in text.split("\n"):
        turn = turn.strip()
        if not turn:
            continue
        body = strip_speaker(turn)
        if not body:
            continue
        chunks = SENT_SPLIT.split(body)
        for c in chunks:
            c = c.strip()
            if c:
                parts.append(c)
    return parts


def align_translations(de_sents: list[str], other: str) -> list[str]:
    """Best-effort: split other the same way; pad/truncate to len(de_sents)."""
    if not other:
        return [""] * len(de_sents)
    other_sents = split_sentences(other)
    if len(other_sents) == len(de_sents):
        return other_sents
    # Fallback: one blob — attach to first sentence only
    if len(other_sents) == 1 and len(de_sents) > 1:
        return [other_sents[0]] + [""] * (len(de_sents) - 1)
    out = []
    for i in range(len(de_sents)):
        out.append(other_sents[i] if i < len(other_sents) else "")
    return out


def lemma_forms(lemma: str, pos: str = "") -> set[str]:
    """Simple surface forms for matching."""
    w = lemma.strip()
    if not w:
        return set()
    forms = {w, w.lower(), w.capitalize()}
    m = re.match(r"^(der|die|das|ein|eine)\s+(.+)$", w, re.I)
    if m:
        forms |= lemma_forms(m.group(2), pos)
        return forms
    low = w.lower()
    pos_l = (pos or "").lower()
    looks_verb = "verb" in pos_l or (
        low[:1].islower() and low.endswith(("en", "eln", "ern")) and len(low) > 3
    )
    if looks_verb:
        if low.endswith("eln"):
            stem = low[:-1]  # wandeln → wandle…
            forms.update({stem, stem + "t", stem + "st", low[:-3] + "le", low[:-3] + "elt"})
        elif low.endswith("ern"):
            stem = low[:-1]
            forms.update({stem, stem + "t", stem + "st"})
        elif low.endswith("en"):
            stem = low[:-2]
            forms.update({stem, stem + "t", stem + "st", stem + "e", stem + "te", stem + "ten"})
    # Light noun plurals (exact-ish), only for capitalized lemmas
    if w[:1].isupper():
        if low.endswith("e") and len(low) > 3:
            forms.add(low + "n")
        if not low.endswith("s"):
            forms.add(low + "s")
        if low.endswith("er"):
            forms.add(low)  # already
    return {f for f in forms if len(f) >= 2}


def sentence_matches(sent: str, forms: set[str], allow_prefix: bool) -> bool:
    tokens = {t.lower() for t in WORD_RE.findall(sent)}
    for f in forms:
        if f.lower() in tokens:
            return True
    if not allow_prefix:
        return False
    # Only extend from short stems already in forms (geh → geht already listed;
    # catch geht's / gehst leftovers via stem+suffix not in the set)
    short = {f.lower() for f in forms if 4 <= len(f) <= 8}
    for t in tokens:
        for st in short:
            if len(t) > len(st) and t.startswith(st) and len(t) - len(st) <= 2:
                # gehend, gehst — avoid matching unrelated longer lemmas
                if t[len(st) :] in {"t", "st", "e", "en", "te", "ten", "est"}:
                    return True
    return False


def is_clean_example(s: str) -> bool:
    s = s.strip()
    if len(s) < MIN_LEN or len(s) > MAX_LEN:
        return False
    if s.count(" ") < 1:
        return False
    if re.search(r"\[|\]|\.{3,}|_{2,}", s):
        return False
    # Reject mid-fragment leftovers from bad splits ("h., man muss…")
    if re.match(r"^[a-zäöüß]", s):
        return False
    if re.match(r"^[A-Za-zäöüÄÖÜß]\.,", s):
        return False
    return True


def load_corpus() -> list[Sentence]:
    corpus: list[Sentence] = []
    for path in sorted(LISTEN.glob("cd*-t*.json")):
        data = json.loads(path.read_text())
        de = data.get("text") or ""
        if not de.strip():
            continue
        lesson = int(data.get("lessonNumber") or 0)
        de_sents = split_sentences(de)
        en_sents = align_translations(de_sents, data.get("textEn") or "")
        fa_sents = align_translations(de_sents, data.get("textFa") or "")
        for i, d in enumerate(de_sents):
            if not is_clean_example(d):
                continue
            corpus.append(
                Sentence(
                    de=d,
                    en=en_sents[i] if i < len(en_sents) else "",
                    fa=fa_sents[i] if i < len(fa_sents) else "",
                    lesson=lesson,
                    track=path.stem,
                )
            )
    return corpus


def build_index(corpus: list[Sentence]) -> dict[str, list[Sentence]]:
    """token → sentences containing that token (lowercase)."""
    idx: dict[str, list[Sentence]] = {}
    for s in corpus:
        for t in {w.lower() for w in WORD_RE.findall(s.de)}:
            idx.setdefault(t, []).append(s)
    return idx


def pick_example(
    lemma: str,
    pos: str,
    lesson_num: int,
    corpus: list[Sentence],
    index: dict[str, list[Sentence]] | None = None,
) -> Sentence | None:
    forms = lemma_forms(lemma, pos)
    if not forms:
        return None
    pos_l = (pos or "").lower()
    allow_prefix = "verb" in pos_l or (
        lemma.strip()[:1].islower() and lemma.strip().lower().endswith(("en", "eln", "ern"))
    )

    candidates: list[Sentence] = []
    if index is not None:
        seen: set[int] = set()
        for f in forms:
            for s in index.get(f.lower(), []):
                sid = id(s)
                if sid in seen:
                    continue
                seen.add(sid)
                candidates.append(s)
        if allow_prefix:
            # also pull sentences for stem-prefixed tokens via scanning forms only
            pass
    else:
        candidates = corpus

    same: list[Sentence] = []
    other: list[Sentence] = []
    for s in candidates:
        if not sentence_matches(s.de, forms, allow_prefix):
            continue
        (same if s.lesson == lesson_num else other).append(s)
    pool = same or other
    if not pool:
        return None
    pool.sort(key=lambda s: (0 if s.lesson == lesson_num else 1, len(s.de), 0 if s.en else 1))
    return pool[0]


def translate_pair(de: str, cache: dict) -> tuple[str, str]:
    from deep_translator import GoogleTranslator

    if de in cache:
        c = cache[de]
        return c.get("en", ""), c.get("fa", "")
    en = GoogleTranslator(source="de", target="en").translate(de) or ""
    time.sleep(0.2)
    fa = GoogleTranslator(source="de", target="fa").translate(de) or ""
    time.sleep(0.2)
    cache[de] = {"en": en.strip(), "fa": fa.strip()}
    return en.strip(), fa.strip()


def load_i18n_cache() -> tuple[Path, dict]:
    cache_path = APP / "scripts" / ".example-i18n-cache.json"
    cache: dict = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
    return cache_path, cache


def retranslate_existing(force: bool = False) -> None:
    """Fix exampleEn/exampleFa by translating exampleDe (alignment is unreliable)."""
    cache_path, cache = load_i18n_cache()
    updated = 0
    for path in sorted(LESSONS.glob("*-l*.json")):
        data = json.loads(path.read_text())
        dirty = False
        for item in data.get("vocab") or []:
            de = (item.get("exampleDe") or "").strip()
            if not de:
                continue
            if (
                not force
                and (item.get("exampleEn") or "").strip()
                and (item.get("exampleFa") or "").strip()
                and de in cache
            ):
                # Already translated via our cache — keep
                continue
            # Always retranslate when force, or when not in our sentence cache
            # (values copied from misaligned track textEn/textFa)
            try:
                en, fa = translate_pair(de, cache)
            except Exception as e:
                print(f"  fail {item.get('de')}: {e}")
                continue
            if en and item.get("exampleEn") != en:
                item["exampleEn"] = en
                dirty = True
            if fa and item.get("exampleFa") != fa:
                item["exampleFa"] = fa
                dirty = True
            updated += 1
            if updated % 50 == 0:
                print(f"  … {updated} sentences", flush=True)
                cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")
        if dirty:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Wrote {path.name}", flush=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")
    print(f"Retranslated {updated} example sentences")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Overwrite existing examples")
    ap.add_argument(
        "--translate-missing",
        action="store_true",
        help="Translate example EN/FA (per-sentence; do not trust track alignment)",
    )
    ap.add_argument(
        "--retranslate-examples",
        action="store_true",
        help="Only re-translate EN/FA for vocab that already has exampleDe",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="Max vocab items to enrich")
    args = ap.parse_args()

    if args.retranslate_examples:
        retranslate_existing(force=True)
        return

    print("Loading listening corpus…")
    corpus = load_corpus()
    index = build_index(corpus)
    print(f"  {len(corpus)} clean sentences, {len(index)} token keys")

    cache_path, cache = load_i18n_cache()

    lesson_files = sorted(LESSONS.glob("*-l*.json"))
    filled = 0
    skipped = 0
    missing = 0
    translated = 0
    processed = 0

    for path in lesson_files:
        data = json.loads(path.read_text())
        lesson_num = int(data.get("number") or 0)
        vocab = data.get("vocab") or []
        dirty = False
        for item in vocab:
            lemma = (item.get("de") or "").strip()
            if not lemma:
                continue
            if item.get("exampleDe") and not args.force:
                skipped += 1
                continue
            if args.limit and processed >= args.limit:
                break
            processed += 1
            hit = pick_example(lemma, item.get("pos") or "", lesson_num, corpus, index)
            if not hit:
                missing += 1
                continue
            en, fa = "", ""
            if args.translate_missing and not args.dry_run:
                try:
                    en, fa = translate_pair(hit.de, cache)
                    translated += 1
                except Exception as e:
                    print(f"  translate fail {lemma}: {e}")
            if args.dry_run:
                print(f"  L{lesson_num} {lemma!r} ← {hit.de[:70]!r} ({hit.track})")
            else:
                item["exampleDe"] = hit.de
                if en:
                    item["exampleEn"] = en
                if fa:
                    item["exampleFa"] = fa
                dirty = True
            filled += 1
        if dirty and not args.dry_run:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"Wrote {path.name}")
        if args.limit and processed >= args.limit:
            break

    if args.translate_missing and not args.dry_run and cache:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")

    print(
        f"Done. filled={filled} skipped_existing={skipped} "
        f"no_match={missing} translated={translated}"
    )


if __name__ == "__main__":
    main()
