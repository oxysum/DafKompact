# DaF kompakt Learning Web App

Personal German study app for **DaF kompakt A1–B1** (German ↔ English).

## Lesson path

Each Lektion: **Goals → Vocabulary → Grammar drills → Quiz** (≥70% unlocks the next lesson).

Optional **Listening** (Hörverstehen): Kursbuch CD tracks + transcripts. Does not gate unlock.

## Run

```bash
# Node 20+ recommended (nvm use 22)
npm install
npm run dev
```

## Content

- `public/content/index.json` — all 30 lessons
- `public/content/lektionen/*.json` — per-lesson data (incl. `listening[]`)
- `public/content/listening/` — per-track transcripts matched to CD1–3
- A1–B1 all 30 lessons complete (vocab, grammar, drills, quiz); listening attached where available
- Vocab lemmas are unique across lessons (see `scripts/dedupe-vocab-across-lessons.py`)
- Example sentences on flashcards come from listening transcripts when possible
  (`scripts/normalize-listening-transcripts.py`, `scripts/enrich-vocab-examples-from-listening.py`)

### Listening audio (local only)

MP3s are **not** in git (copyright). With the Kursbuch CD folders next to this app:

```bash
python3 scripts/parse-transcriptions.py
```

That writes hard links under `public/audio/cd{n}/track-{nn}.mp3`.

## Notes

- Progress is stored in `localStorage` (export/import under Settings).
- **Helper language** (Settings): English (default) or فارسی for meanings; German stays the learning language. Missing Farsi falls back to English.
- For personal study only — do not redistribute copyrighted book text or audio.
