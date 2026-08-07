#!/usr/bin/env python3
"""Attach Commons De-*.ogg pronunciations to vocab via batched titles queries."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "public" / "content" / "lektionen"
AUDIO_DIR = ROOT / "public" / "audio" / "vocab"
CACHE_PATH = Path(__file__).resolve().parent / ".audio-cache.json"
USER_AGENT = "DafKompaktApp/1.0 (personal DaF study; batched Commons titles)"
REQUEST_GAP = 2.0
BATCH = 40  # titles per request (max 50)
SSL_CTX = ssl.create_default_context(cafile=certifi.where())
_last_req = 0.0


def throttle() -> None:
    global _last_req
    now = time.time()
    wait = REQUEST_GAP - (now - _last_req)
    if wait > 0:
        time.sleep(wait)
    _last_req = time.time()


def normalize_de(de: str) -> str:
    return re.sub(r"\s+", " ", de.replace("\u00ad", "").strip())


def slugify(de: str) -> str:
    s = normalize_de(de).lower()
    s = re.sub(r"^(der|die|das)\s+", "", s, flags=re.I)
    s = re.sub(r"[^\w\-äöüß]+", "-", s, flags=re.UNICODE)
    return re.sub(r"-+", "-", s).strip("-")[:80] or "word"


def lemma_forms(de: str) -> list[str]:
    s = normalize_de(de)
    s = re.sub(r"^(der|die|das)\s+", "", s, flags=re.I)
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(".,;:!?")
    forms: list[str] = []
    seen: set[str] = set()

    def add(x: str) -> None:
        x = x.strip()
        if x and x not in seen and re.match(r"^[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\-]*$", x):
            seen.add(x)
            forms.append(x)

    if not s:
        return forms
    add(s)
    m = re.match(r"^([A-Za-zÄÖÜäöüß\-]+)", s)
    if m:
        add(m.group(1))
    if " " in s:
        add(s.split()[0].rstrip(".,;:"))
    for f in list(forms):
        add(f[0].swapcase() + f[1:])
    return forms


def clean_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def commons_md5_url(filename: str) -> str:
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode()).hexdigest()
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/"
        f"{h[0]}/{h[:2]}/{urllib.parse.quote(name)}"
    )


def http_json(url: str) -> dict | None:
    delay = 30.0
    for _ in range(12):
        throttle()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                print(f"  429 — sleep {delay:.0f}s")
                time.sleep(delay)
                delay = min(delay * 1.5, 360)
                continue
            print(f"  HTTP {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"  net {e} — sleep {delay:.0f}s")
            time.sleep(delay)
            delay = min(delay * 1.5, 180)
    return None


def load_cache() -> dict:
    if CACHE_PATH.is_file():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def cache_hit(cache: dict, de: str) -> dict | None:
    if de in cache:
        e = cache[de]
        if e.get("miss"):
            return None
        if e.get("file") and (e.get("url") or e.get("commonsUrl")):
            return {
                "file": e["file"],
                "url": e.get("url") or e["commonsUrl"],
            }
    for f in lemma_forms(de):
        e = cache.get(f"lemma:{f}")
        if e and e.get("file") and (e.get("url") or e.get("commonsUrl")):
            return {"file": e["file"], "url": e.get("url") or e["commonsUrl"]}
    return None


def cache_known_miss(cache: dict, de: str) -> bool:
    if cache.get(de, {}).get("miss"):
        return True
    forms = lemma_forms(de)
    if not forms:
        return True
    return all(cache.get(f"lemma:{f}", {}).get("miss") for f in forms)


def batch_probe(forms: list[str]) -> dict[str, dict | None]:
    """Map lemma form → {file,url} or None (miss). Transient failure → omit key."""
    titles: list[str] = []
    title_to_form: dict[str, str] = {}
    for f in forms:
        for name in (f"De-{f}.ogg", f"De-{f}.OGG"):
            t = f"File:{name}"
            titles.append(t)
            title_to_form[t.replace("_", " ")] = f
            title_to_form[t] = f

    # chunk
    out: dict[str, dict | None] = {f: None for f in forms}
    found: dict[str, dict] = {}

    for i in range(0, len(titles), BATCH):
        chunk = titles[i : i + BATCH]
        params = {
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        }
        url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
            params
        )
        data = http_json(url)
        if not data:
            # transient — remove defaults so caller knows
            return {}
        pages = (data.get("query") or {}).get("pages") or {}
        for page in pages.values():
            title = page.get("title") or ""
            # title like "File:De-Haus.ogg"
            if "missing" in page:
                continue
            infos = page.get("imageinfo") or []
            if not infos or not infos[0].get("url"):
                continue
            fname = title.split(":", 1)[-1]
            # map back to form
            form = None
            m = re.match(r"^De-(.+)\.(ogg|OGG)$", fname)
            if m:
                form = m.group(1)
            if not form:
                continue
            # prefer exact case match in our forms list
            url_c = clean_url(infos[0]["url"])
            # find matching form ignoring case
            match_form = next(
                (f for f in forms if f.lower() == form.lower()), form
            )
            prev = found.get(match_form)
            # prefer .ogg over .OGG already same; prefer exact case
            if not prev or form == match_form:
                found[match_form] = {"file": fname, "url": url_c}

    for f in forms:
        out[f] = found.get(f) or found.get(
            next((k for k in found if k.lower() == f.lower()), ""), None
        )
        if out[f] is None and f not in found:
            # confirmed miss only if we got a successful response
            out[f] = None  # miss
    return out


def ensure_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def convert_to_mp3(src: Path, dest: Path) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-vn",
                "-acodec",
                "libmp3lame",
                "-q:a",
                "4",
                str(dest),
            ],
            check=True,
            capture_output=True,
        )
        return dest.is_file() and dest.stat().st_size > 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def download(url: str, dest: Path) -> bool:
    throttle()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
            data = resp.read()
        if len(data) < 100:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass

    cache = load_cache()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    has_ffmpeg = ensure_ffmpeg()

    words: set[str] = set()
    lesson_paths = sorted(CONTENT.glob("*.json"))
    for path in lesson_paths:
        data = json.loads(path.read_text())
        for v in data.get("vocab") or []:
            if v.get("de"):
                words.add(normalize_de(v["de"]))

    word_list = sorted(words)
    print(f"Unique vocab: {len(word_list)}")

    # Collect forms still needing lookup
    pending_forms: list[str] = []
    pending_seen: set[str] = set()
    for de in word_list:
        if cache_hit(cache, de) is not None or cache_known_miss(cache, de):
            continue
        for f in lemma_forms(de):
            key = f"lemma:{f}"
            if key in cache or f.lower() in pending_seen:
                continue
            pending_seen.add(f.lower())
            pending_forms.append(f)

    print(f"Forms to probe: {len(pending_forms)}")

    # Batch probe
    for i in range(0, len(pending_forms), 20):
        chunk = pending_forms[i : i + 20]
        result = batch_probe(chunk)
        if not result:
            print("  batch failed (rate limit) — saving and stopping probes")
            save_cache(cache)
            break
        for form, hit in result.items():
            key = f"lemma:{form}"
            if hit:
                cache[key] = hit
            else:
                cache[key] = {"miss": True}
        # also mark de keys when we can
        if (i // 20) % 5 == 0:
            print(f"  probed {min(i+20, len(pending_forms))}/{len(pending_forms)}")
            save_cache(cache)

    save_cache(cache)

    # Map words → audio URL
    audio_by_de: dict[str, str] = {}
    local_n = remote_n = missed = 0
    commons_ok = True

    for de in word_list:
        slug = slugify(de)
        dest = AUDIO_DIR / f"{slug}.mp3"
        local_url = f"/audio/vocab/{slug}.mp3"
        if dest.is_file() and dest.stat().st_size > 0:
            audio_by_de[de] = local_url
            local_n += 1
            continue

        hit = cache_hit(cache, de)
        if not hit:
            # try resolve from lemma cache freshly
            for f in lemma_forms(de):
                e = cache.get(f"lemma:{f}")
                if e and e.get("file"):
                    hit = {
                        "file": e["file"],
                        "url": e.get("url") or e.get("commonsUrl"),
                    }
                    cache[de] = hit
                    break
            if not hit:
                if cache_known_miss(cache, de) or all(
                    cache.get(f"lemma:{f}", {}).get("miss") for f in lemma_forms(de)
                ):
                    cache[de] = {"miss": True}
                missed += 1
                continue

        remote = hit["url"]
        if has_ffmpeg and commons_ok:
            ext = Path(hit["file"]).suffix or ".ogg"
            raw = AUDIO_DIR / f"{slug}.src{ext}"
            if download(remote, raw) and convert_to_mp3(raw, dest):
                raw.unlink(missing_ok=True)
                audio_by_de[de] = local_url
                local_n += 1
                continue
            raw.unlink(missing_ok=True)
            commons_ok = False

        audio_by_de[de] = remote
        remote_n += 1

    save_cache(cache)

    writes = cleared = lessons = 0
    for path in lesson_paths:
        data = json.loads(path.read_text())
        changed = False
        for v in data.get("vocab") or []:
            de = normalize_de(v.get("de") or "")
            url = audio_by_de.get(de)
            if url:
                if v.get("audioUrl") != url:
                    v["audioUrl"] = url
                    changed = True
                    writes += 1
            elif "audioUrl" in v:
                del v["audioUrl"]
                changed = True
                cleared += 1
        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            lessons += 1

    total = len(word_list)
    covered = len(audio_by_de)
    print(
        f"Done. Coverage: {covered}/{total} ({100*covered/total:.1f}%) "
        f"local={local_n} remote={remote_n} miss={missed}. "
        f"Lessons={lessons} writes={writes}."
    )


if __name__ == "__main__":
    main()
