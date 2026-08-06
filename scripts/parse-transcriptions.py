#!/usr/bin/env python3
"""
Parse DaF kompakt Kursbuch Transkriptionen and match to CD MP3 tracks.

Outputs:
  public/content/listening/index.json
  public/content/listening/cd{n}-t{nn}.json
  public/content/listening/by-lesson.json
  public/content/listening/mismatch-report.json
  public/audio/cd{n}/track-{nn}.mp3  (symlinks)
  Updates each lesson JSON with a listening[] array
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

ROOT = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt")
APP = ROOT / "daf-kompakt-app"
TRANSCRIPT_PDF = ROOT / "A08103-67618001_DaFkompakt_Transkriptionen_KB_EB.pdf"
OCR_PDF = ROOT / "DaF-kompakt-A1-B1-KB-ocr.pdf"
AUDIO_SRC = ROOT / "cd" / "DaF kompakt A1-B1 kursbuch"
OUT_LISTEN = APP / "public" / "content" / "listening"
OUT_AUDIO = APP / "public" / "audio"
LESSONS_DIR = APP / "public" / "content" / "lektionen"

# Track marker: "1 1" / "2 12" — CD, four-per-em space (U+2005), track, then tab/space.
# Do NOT treat bare "13.00" / page "11" as markers (those lack U+2005).
TRACK_RE = re.compile(
    r"(?:^|\n)\s*([123])\s*\u2005\s*(\d{1,2})(?:\t|\s)",
    re.MULTILINE,
)
LEKTION_RE = re.compile(r"(?:^|\n)\s*Lektion\s+(\d+)\b", re.IGNORECASE)


def lesson_id(n: int) -> str:
    if n <= 8:
        return f"a1-l{n:02d}"
    if n <= 18:
        return f"a2-l{n:02d}"
    return f"b1-l{n:02d}"


def extract_pdf_text(path: Path, start_page: int | None = None) -> str:
    r = PdfReader(str(path))
    pages = r.pages
    if start_page is not None:
        pages = pages[start_page:]
    parts = []
    for p in pages:
        parts.append(p.extract_text() or "")
    return "\n".join(parts)


def clean_text(s: str) -> str:
    s = s.replace("\u00ad", "")  # soft hyphen
    s = s.replace("\t", " ")
    s = re.sub(r"[ \u2005\u00a0\u2009]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def parse_tracks(blob: str) -> list[dict]:
    """Return list of {cd, track, lessonNumber, text, preview}."""
    # Find all Lektion positions
    lek_spans = [(m.start(), int(m.group(1))) for m in LEKTION_RE.finditer(blob)]
    track_matches = list(TRACK_RE.finditer(blob))

    def lesson_at(pos: int) -> int | None:
        cur = None
        for start, num in lek_spans:
            if start <= pos:
                cur = num
            else:
                break
        return cur

    items = []
    for i, m in enumerate(track_matches):
        cd = int(m.group(1))
        track = int(m.group(2))
        if track < 1 or track > 99:
            continue
        start = m.end()
        end = track_matches[i + 1].start() if i + 1 < len(track_matches) else len(blob)
        raw = blob[start:end]
        # Strip trailing Lektion header if present at end of chunk
        raw = re.sub(r"\n\s*Lektion\s+\d+\s*$", "", raw, flags=re.I)
        # Strip leading CD header remnants
        raw = re.sub(r"^\s*CD\s+[123]\s*", "", raw)
        text = clean_text(raw)
        if not text:
            continue
        # Drop running headers / OCR junk
        text = re.sub(r"(?m)^TranskriptionenT?\s*$", "", text).strip()
        if not text or text.lower().startswith("transkriptionen"):
            continue
        preview = text.split("\n", 1)[0][:120]
        items.append(
            {
                "cd": cd,
                "track": track,
                "lessonNumber": lesson_at(m.start()),
                "text": text,
                "preview": preview,
                "id": f"cd{cd}-t{track:02d}",
                "audioUrl": f"/audio/cd{cd}/track-{track:02d}.mp3",
            }
        )

    # Dedupe by cd+track keeping first occurrence (markers are unique when regex is tight)
    by_key: dict[tuple[int, int], dict] = {}
    for it in items:
        key = (it["cd"], it["track"])
        if key not in by_key:
            by_key[key] = it
        elif len(it["text"]) > len(by_key[key]["text"]) * 1.5:
            # Prefer much longer body only if first was truncated at a page break
            by_key[key] = it
    return [by_key[k] for k in sorted(by_key.keys())]


def find_mp3(cd: int, track: int) -> Path | None:
    folder = AUDIO_SRC / str(cd)
    if not folder.is_dir():
        return None
    # Prefer "NN Track N.mp3"
    candidates = [
        folder / f"{track:02d} Track {track}.mp3",
        folder / f"{track:02d} Track {track}.MP3",
        folder / f"{track} Track {track}.mp3",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fuzzy: any file containing Track N
    for p in folder.glob("*.mp3"):
        m = re.search(r"Track\s+(\d+)", p.name, re.I)
        if m and int(m.group(1)) == track:
            return p
    return None


def link_or_copy(src: Path, dest: Path) -> None:
    """Prefer hard link (same volume); fall back to copy. Avoid external symlinks —
    Vite refuses to serve them from public/ and the player stays at 0:00/0:00."""
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        import shutil

        shutil.copy2(src, dest)


def symlink_audio(tracks: list[dict]) -> dict:
    report = {"linked": [], "missing_mp3": [], "orphan_mp3": []}
    OUT_AUDIO.mkdir(parents=True, exist_ok=True)

    linked_keys = set()
    for it in tracks:
        src = find_mp3(it["cd"], it["track"])
        dest_dir = OUT_AUDIO / f"cd{it['cd']}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"track-{it['track']:02d}.mp3"
        if src is None:
            report["missing_mp3"].append({"cd": it["cd"], "track": it["track"]})
            continue
        link_or_copy(src.resolve(), dest)
        linked_keys.add((it["cd"], it["track"]))
        report["linked"].append(
            {"cd": it["cd"], "track": it["track"], "src": str(src), "dest": str(dest)}
        )

    # Orphans: mp3 without transcript
    for cd in (1, 2, 3):
        folder = AUDIO_SRC / str(cd)
        if not folder.is_dir():
            continue
        for p in folder.glob("*.mp3"):
            m = re.search(r"Track\s+(\d+)", p.name, re.I)
            if not m:
                continue
            track = int(m.group(1))
            if (cd, track) not in linked_keys:
                dest_dir = OUT_AUDIO / f"cd{cd}"
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / f"track-{track:02d}.mp3"
                if not dest.exists():
                    link_or_copy(p.resolve(), dest)
                report["orphan_mp3"].append({"cd": cd, "track": track, "file": p.name})

    return report


def update_lessons(tracks: list[dict]) -> None:
    by_lesson: dict[int, list[dict]] = defaultdict(list)
    for it in tracks:
        n = it.get("lessonNumber")
        if not n:
            continue
        by_lesson[n].append(
            {
                "id": it["id"],
                "cd": it["cd"],
                "track": it["track"],
                "audioUrl": it["audioUrl"],
                "preview": it["preview"],
            }
        )

    OUT_LISTEN.mkdir(parents=True, exist_ok=True)
    (OUT_LISTEN / "by-lesson.json").write_text(
        json.dumps({str(k): v for k, v in sorted(by_lesson.items())}, ensure_ascii=False, indent=2)
        + "\n"
    )

    for n in range(1, 31):
        lid = lesson_id(n)
        path = LESSONS_DIR / f"{lid}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        data["listening"] = by_lesson.get(n, [])
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"  {lid}: {len(data['listening'])} tracks")


def main() -> None:
    print("Extracting dedicated Transkriptionen PDF…")
    blob = extract_pdf_text(TRANSCRIPT_PDF)
    tracks = parse_tracks(blob)
    print(f"Parsed {len(tracks)} tracks from dedicated PDF")

    # If sparse, supplement from OCR pages 274–308 (0-index 273:)
    if len(tracks) < 150:
        print("Supplementing from OCR PDF pages 274–308…")
        ocr = extract_pdf_text(OCR_PDF, start_page=273)
        extra = parse_tracks(ocr)
        by = {(t["cd"], t["track"]): t for t in tracks}
        for t in extra:
            key = (t["cd"], t["track"])
            if key not in by or len(t["text"]) > len(by[key]["text"]):
                by[key] = t
        tracks = [by[k] for k in sorted(by.keys())]
        print(f"Combined tracks: {len(tracks)}")

    OUT_LISTEN.mkdir(parents=True, exist_ok=True)
    for it in tracks:
        (OUT_LISTEN / f"{it['id']}.json").write_text(
            json.dumps(it, ensure_ascii=False, indent=2) + "\n"
        )

    index = {
        "source": str(TRANSCRIPT_PDF.name),
        "trackCount": len(tracks),
        "tracks": [
            {
                "id": t["id"],
                "cd": t["cd"],
                "track": t["track"],
                "lessonNumber": t["lessonNumber"],
                "audioUrl": t["audioUrl"],
                "preview": t["preview"],
            }
            for t in tracks
        ],
    }
    (OUT_LISTEN / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n"
    )

    print("Linking MP3s…")
    report = symlink_audio(tracks)
    (OUT_LISTEN / "mismatch-report.json").write_text(
        json.dumps(
            {
                "linked": len(report["linked"]),
                "missing_mp3": report["missing_mp3"],
                "orphan_mp3": report["orphan_mp3"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(
        f"Linked {len(report['linked'])}, missing {len(report['missing_mp3'])}, "
        f"orphans {len(report['orphan_mp3'])}"
    )

    print("Updating lesson JSON listening arrays…")
    update_lessons(tracks)
    print("Done.")


if __name__ == "__main__":
    main()
