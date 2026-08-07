#!/usr/bin/env python3
"""Add Farsi (fa) glosses to lesson vocab from the Deutsch→Persisch Anki deck."""
from __future__ import annotations

import json
import re
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt")
APP = ROOT / "daf-kompakt-app"
CONTENT = APP / "public" / "content" / "lektionen"
ANKI = ROOT / "Daf_kompakt_A1-B1_Deutsch_to_Persisch.apkg"
PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")


def extract_fa(back: str) -> str | None:
    """Back looks like: 'der,- , سرایدار' or 'die, en, انجمن'."""
    # Strip HTML
    back = re.sub(r"<br\s*/?>", " ", back, flags=re.I)
    back = re.sub(r"<[^>]+>", " ", back)
    back = back.replace("&nbsp;", " ").replace("&nbsp", " ")
    back = back.replace("&amp;", "&")
    if not PERSIAN_RE.search(back):
        return None
    parts = [p.strip() for p in re.split(r"[,;/|]", back) if p.strip()]
    fa_parts = [p for p in parts if PERSIAN_RE.search(p)]
    if not fa_parts:
        m = PERSIAN_RE.search(back)
        if not m:
            return None
        fa = back[m.start() :].strip(" ,;/-")
        return clean_fa(fa) or None
    fa = "، ".join(fa_parts)
    return clean_fa(fa) or None


def clean_fa(fa: str) -> str:
    fa = re.sub(r"\s+", " ", fa).strip(" ,;/-")
    fa = fa.replace("&nbsp;", " ").replace("&nbsp", " ")
    return fa.strip()


def load_anki_fa() -> dict[str, str]:
    tmp = Path("/tmp/anki-fa-enrich")
    tmp.mkdir(exist_ok=True)
    with zipfile.ZipFile(ANKI) as z:
        z.extract("collection.anki2", tmp)
    con = sqlite3.connect(tmp / "collection.anki2")
    cur = con.cursor()
    by: dict[str, str] = {}
    for (flds,) in cur.execute("select flds from notes"):
        parts = flds.split("\x1f")
        front = (parts[0] or "").strip()
        back = (parts[1] or "").strip() if len(parts) > 1 else ""
        if not front or PERSIAN_RE.search(front):
            continue
        de = front.replace("\u00ad", "").strip()
        if not re.match(r"^[A-Za-zÄÖÜäöüß\- ]+$", de):
            continue
        fa = extract_fa(back)
        if not fa:
            continue
        k = de.lower()
        # Prefer longer/more complete FA if duplicate
        if k not in by or len(fa) > len(by[k]):
            by[k] = fa
    con.close()
    return by


def lemma_key(de: str) -> str:
    s = de.strip()
    s = re.sub(r"^(der|die|das)\s+", "", s, flags=re.I)
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def main() -> None:
    print("Loading Anki FA map…")
    fa_map = load_anki_fa()
    print(f"Lemmas with Farsi: {len(fa_map)}")

    updated_lessons = 0
    updated_words = 0
    missing = 0

    for path in sorted(CONTENT.glob("*.json")):
        data = json.loads(path.read_text())
        vocab = data.get("vocab") or []
        changed = False
        for v in vocab:
            de = v.get("de") or ""
            key = lemma_key(de)
            fa = fa_map.get(key)
            if not fa and " " not in key:
                # try without trailing punctuation
                fa = fa_map.get(key.rstrip(".,;:"))
            if fa:
                if v.get("fa") != fa:
                    v["fa"] = fa
                    changed = True
                    updated_words += 1
            else:
                missing += 1
        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            updated_lessons += 1
            print(f"  {path.name}: updated")

    print(
        f"Done. Lessons touched: {updated_lessons}, "
        f"vocab fa writes: {updated_words}, still missing fa: {missing}"
    )


if __name__ == "__main__":
    main()
