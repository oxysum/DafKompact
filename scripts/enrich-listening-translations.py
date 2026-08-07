#!/usr/bin/env python3
"""
Add English and Farsi translations to listening track JSON files.

Writes textEn / textFa on each public/content/listening/cd*-t*.json
Uses GoogleTranslator with a local cache. Re-run safely (skips filled fields).
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

APP = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt/daf-kompakt-app")
LISTEN = APP / "public" / "content" / "listening"
CACHE = APP / "scripts" / ".listening-i18n-cache.json"
PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
SPEAKER_RE = re.compile(r"^([^:\n]{1,40}):\s*(.*)$")


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {"en": {}, "fa": {}}


def save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def chunk_text(text: str, max_len: int = 3500) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for line in text.split("\n"):
        add = len(line) + 1
        if buf and size + add > max_len:
            parts.append("\n".join(buf))
            buf = [line]
            size = add
        else:
            buf.append(line)
            size += add
    if buf:
        parts.append("\n".join(buf))
    return parts


def translate_block(text: str, target: str, cache: dict, translators: dict) -> str:
    key = text.strip()
    if not key:
        return ""
    bucket = cache.setdefault(target, {})
    if key in bucket and bucket[key]:
        return bucket[key]

    out_chunks: list[str] = []
    t = translators[target]
    for chunk in chunk_text(text):
        for attempt in range(4):
            try:
                translated = t.translate(chunk)
                if not isinstance(translated, str):
                    translated = str(translated)
                out_chunks.append(translated.strip())
                break
            except Exception as e:
                wait = 1.2 * (attempt + 1)
                print(f"  retry {target} ({attempt+1}): {e} sleep {wait}s", flush=True)
                time.sleep(wait)
        else:
            out_chunks.append(chunk)  # fallback: leave German
        time.sleep(0.25)

    result = "\n".join(out_chunks).strip()
    # Light cleanup for FA: drop accidental HTML
    if target == "fa":
        result = re.sub(r"<[^>]+>", " ", result)
        result = result.replace("&nbsp;", " ")
        result = re.sub(r"\s+\n", "\n", result)
    bucket[key] = result
    save_cache(cache)
    return result


def translate_preserving_speakers(
    text: str, target: str, cache: dict, translators: dict
) -> str:
    """Translate dialogue lines; keep speaker labels as-is when possible."""
    lines = text.split("\n")
    # Prefer whole-block translate for fluency, then try to reattach if counts match
    block = translate_block(text, target, cache, translators)
    # If structure looks reasonable, use block translation
    if block.count(":") >= max(1, text.count(":") // 2):
        return block

    # Fallback: line-by-line for dialogue-heavy tracks
    out: list[str] = []
    for line in lines:
        m = SPEAKER_RE.match(line.strip())
        if m and m.group(2).strip():
            speaker, body = m.group(1).strip(), m.group(2).strip()
            body_tr = translate_block(body, target, cache, translators)
            out.append(f"{speaker}: {body_tr}")
        elif line.strip():
            out.append(translate_block(line.strip(), target, cache, translators))
        else:
            out.append("")
    return "\n".join(out).strip()


def main() -> None:
    cache = load_cache()
    translators = {
        "en": GoogleTranslator(source="de", target="en"),
        "fa": GoogleTranslator(source="de", target="fa"),
    }
    files = sorted(LISTEN.glob("cd*-t*.json"))
    print(f"Tracks: {len(files)}", flush=True)

    done = skipped = 0
    for i, path in enumerate(files, 1):
        data = json.loads(path.read_text())
        text = (data.get("text") or "").strip()
        if not text:
            continue
        need_en = not (data.get("textEn") or "").strip()
        need_fa = not (data.get("textFa") or "").strip()
        if not need_en and not need_fa:
            skipped += 1
            continue

        print(f"[{i}/{len(files)}] {path.name} ({len(text)} chars)", flush=True)
        if need_en:
            data["textEn"] = translate_preserving_speakers(
                text, "en", cache, translators
            )
        if need_fa:
            data["textFa"] = translate_preserving_speakers(
                text, "fa", cache, translators
            )
            if data["textFa"] and not PERSIAN_RE.search(data["textFa"]):
                print(f"  warn: FA missing Persian script for {path.name}", flush=True)

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        done += 1

    # coverage
    with_en = with_fa = 0
    for path in files:
        d = json.loads(path.read_text())
        if (d.get("textEn") or "").strip():
            with_en += 1
        if (d.get("textFa") or "").strip() and PERSIAN_RE.search(d["textFa"]):
            with_fa += 1
    print(
        f"Done. Updated {done}, skipped {skipped}. "
        f"Coverage EN {with_en}/{len(files)}, FA {with_fa}/{len(files)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
