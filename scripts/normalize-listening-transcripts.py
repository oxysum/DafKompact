#!/usr/bin/env python3
"""
Normalize listening transcripts: join PDF soft line-wraps inside speaker turns.

Example (before):
  Fr. May: … Aufgaben sind nicht
  schwer. Also: Der Tag …

After:
  Fr. May: … Aufgaben sind nicht schwer. Also: Der Tag …

Optionally re-translates textEn/textFa when German text changes (--retranslate).
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
LISTEN = APP / "public" / "content" / "listening"

SPEAKER_RE = re.compile(r"^([^:\n]{1,48}):\s*(.*)$")
SENT_END_RE = re.compile(r'[.!?…»"”\']\s*$')
HYPHEN_WRAP_RE = re.compile(r"(\w)-\s*\n\s*(\w)", re.UNICODE)


# Discourse markers / connectors that appear as "Also:" mid-transcript — not speakers
FALSE_SPEAKERS = {
    "also",
    "aber",
    "und",
    "dann",
    "denn",
    "oder",
    "ja",
    "nein",
    "okay",
    "o.k.",
    "ok",
    "na",
    "naja",
    "ach",
    "so",
    "nun",
    "jetzt",
    "hier",
    "dort",
    "bitte",
    "danke",
    "entschuldigung",
    "moment",
    "beispiel",
    "zum beispiel",
}
TITLE_ABBR = frozenset({"fr", "hr", "dr", "prof", "mr", "mrs", "ms", "nr", "st"})


def is_speaker_line(line: str) -> bool:
    """True only for dialogue labels like 'Sylvie:' / 'Fr. May:', not 'Also:' mid-sentence."""
    m = SPEAKER_RE.match(line.strip())
    if not m:
        return False
    speaker = m.group(1).strip()
    if not speaker or len(speaker) > 40:
        return False
    if re.search(r"\d{2}:\d{2}", speaker):
        return False
    if speaker.lower() in FALSE_SPEAKERS:
        return False
    # Mid-sentence "schwer. Also:" — period + space + word, unless title abbr (Fr. May)
    for mdot in re.finditer(r"(\w+)\.\s+(\S)", speaker):
        if mdot.group(1).lower() not in TITLE_ABBR:
            return False
    # Must start with a capital letter (names / titles)
    if not re.match(r"^[A-ZÄÖÜ]", speaker):
        return False
    # Reject if any token starts lowercase (wrapped content), ignore title abbrs
    for tok in re.split(r"[\s.]+", speaker):
        if not tok:
            continue
        if tok.lower() in TITLE_ABBR:
            continue
        if tok[0].islower() and len(tok) >= 2:
            return False
    return True


def join_soft_wraps(text: str) -> str:
    if not text or "\n" not in text:
        return text

    text = HYPHEN_WRAP_RE.sub(r"\1\2", text)
    raw_lines = text.split("\n")
    turns: list[str] = []
    buf: list[str] = []

    def flush_buf() -> None:
        nonlocal buf
        if not buf:
            return
        merged = buf[0].strip()
        for piece in buf[1:]:
            piece = piece.strip()
            if not piece:
                continue
            if merged.endswith("-") and piece[:1].islower():
                merged = merged[:-1] + piece
            elif SENT_END_RE.search(merged):
                merged = merged + " " + piece
            else:
                merged = merged + " " + piece
        turns.append(merged)
        buf = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            flush_buf()
            continue
        if is_speaker_line(stripped):
            flush_buf()
            buf = [stripped]
        else:
            if buf:
                buf.append(stripped)
            else:
                buf = [stripped]
    flush_buf()

    return "\n".join(turns)


def normalize_track_text(text: str) -> str:
    out = join_soft_wraps(text)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" *\n *", "\n", out)
    return out.strip()


def retranslate(text: str) -> tuple[str, str]:
    from deep_translator import GoogleTranslator

    en = GoogleTranslator(source="de", target="en").translate(text)
    time.sleep(0.3)
    fa = GoogleTranslator(source="de", target="fa").translate(text)
    time.sleep(0.3)
    return (en or "").strip(), (fa or "").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--retranslate",
        action="store_true",
        help="Re-translate textEn/textFa when German text changes",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(LISTEN.glob("cd*-t*.json"))
    changed = 0
    for path in files:
        data = json.loads(path.read_text())
        original = data.get("text") or ""
        if not original.strip():
            continue
        normalized = normalize_track_text(original)
        if normalized == original.strip():
            continue
        changed += 1
        print(f"{path.name}: joined wraps ({len(original)} → {len(normalized)} chars)")
        if args.dry_run:
            if "Fr. May" in normalized:
                i = normalized.find("Fr. May")
                print("  sample:", normalized[i : i + 200])
            continue
        data["text"] = normalized
        first = normalized.split("\n", 1)[0]
        data["preview"] = first[:80] + ("…" if len(first) > 80 else "")
        if args.retranslate:
            try:
                en, fa = retranslate(normalized)
                if en:
                    data["textEn"] = en
                if fa:
                    data["textFa"] = fa
                print("  retranslated EN/FA")
            except Exception as e:
                print(f"  retranslate failed: {e}")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    print(f"Done. Tracks with soft wraps fixed: {changed}/{len(files)}")


if __name__ == "__main__":
    main()
