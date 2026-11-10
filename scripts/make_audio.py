#!/usr/bin/env python3
"""Makes an AI-voiced narration of one essay: python3 scripts/make_audio.py <slug>

Offline, CPU only. Uses kokoro-onnx (no torch). Each text chunk is synthesized in its own
subprocess, so a crash in the native code loses one chunk (retried), not the whole essay.
The chunks are joined with short pauses and encoded to mono Opus with ffmpeg, then written to
audio/<slug>.opus. build.py copies audio/ to docs/audio/ and shows a player only for essays
that have a file there.

Setup (once):
  pip install kokoro-onnx soundfile numpy      # also needs ffmpeg with libopus
  mkdir -p ~/kokoro && cd ~/kokoro
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  export KOKORO_DIR=~/kokoro                   # or pass --model-dir

Narration text comes from content/posts/<slug>.html (sources list left out). The published essay
is never changed. Listen to the result before committing it.
"""
import argparse
import html
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_CHARS = 280
RETRIES = 3
TIMEOUT = 180
PAUSE = {"para": 0.55, "heading": 0.9, "sentence": 0.25}  # seconds of silence after a chunk
VOICE = "af_heart"
SPEED = 1.0

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def two(n):
    if n < 20:
        return ONES[n]
    return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])


def year(m):
    y = int(m.group(0))
    a, b = divmod(y, 100)
    if 2000 <= y <= 2009:
        return "two thousand" + ("" if b == 0 else " " + ONES[b])
    if b == 0:
        return two(a) + " hundred"
    return two(a) + " " + ("oh " + ONES[b] if b < 10 else two(b))


def normalize(text):
    text = html.unescape(text)
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)  # dashes read as a short pause
    text = re.sub(r"\bU\.S\.A?\.?(?=\W|$)", "United States", text)
    text = re.sub(r"\bFPTP\b", "first past the post", text)
    text = re.sub(r"\bSTAR\b", "Star", text)
    text = re.sub(r"\be\.g\.,?", "for example,", text)
    text = re.sub(r"\bi\.e\.,?", "that is,", text)
    text = re.sub(r"\betc\.", "and so on.", text)
    text = re.sub(r"\bvs\.?", "versus", text)
    text = re.sub(r"\bDr\.", "Doctor", text)
    text = text.replace("hoto.lol", "hoto dot lol")
    text = re.sub(r"\bAOC\b", "A O C", text)
    text = re.sub(r"\bAI\b", "A I", text)
    text = re.sub(r"(\d+)\s*%", r"\1 percent", text)
    text = text.replace("&", " and ")
    text = re.sub(r"\b(1[5-9]\d\d|20\d\d)\b", year, text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def blocks(raw):
    """Yields (text, pause_after) for headings, paragraphs and list items."""
    raw = raw.split('id="sources"')[0]
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S)
    for m in re.finditer(r"<(h[1-6]|p|li|blockquote)\b[^>]*>(.*?)</\1>", raw, flags=re.S):
        tag, inner = m.group(1), m.group(2)
        if "<p" in inner and tag == "blockquote":
            continue  # its paragraphs are picked up on their own
        t = normalize(re.sub(r"<[^>]+>", " ", inner))
        if not t:
            continue
        if tag.startswith("h"):
            yield (t if t[-1] in ".!?" else t + "."), "heading"
        else:
            yield t, "para"


def split_long(sentence):
    """Breaks an over-long sentence at commas, semicolons or colons, then spaces."""
    out, cur = [], ""
    for piece in re.split(r"(?<=[,;:])\s+", sentence):
        while len(piece) > MAX_CHARS:
            cut = piece.rfind(" ", 0, MAX_CHARS)
            cut = cut if cut > 0 else MAX_CHARS
            if cur:
                out.append(cur)
                cur = ""
            out.append(piece[:cut])
            piece = piece[cut:].strip()
        if len(cur) + len(piece) + 1 <= MAX_CHARS:
            cur = (cur + " " + piece).strip()
        else:
            out.append(cur)
            cur = piece
    if cur:
        out.append(cur)
    return out


def chunks(raw):
    """List of (chunk_text, pause_after_seconds). Pause applies after the last chunk of a block."""
    result = []
    for text, kind in blocks(raw):
        sentences = re.split(r"(?<=[.!?])[\"')\]]*\s+", text)
        parts, cur = [], ""
        for s in sentences:
            for piece in (split_long(s) if len(s) > MAX_CHARS else [s]):
                if len(cur) + len(piece) + 1 <= MAX_CHARS:
                    cur = (cur + " " + piece).strip()
                else:
                    parts.append(cur)
                    cur = piece
        if cur:
            parts.append(cur)
        for i, part in enumerate(parts):
            result.append((part, PAUSE[kind] if i == len(parts) - 1 else PAUSE["sentence"]))
    return result


def worker(model_dir, text, out):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(str(pathlib.Path(model_dir) / "kokoro-v1.0.onnx"), str(pathlib.Path(model_dir) / "voices-v1.0.bin"))
    samples, rate = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    if len(samples) == 0:
        sys.exit("empty audio")
    sf.write(out, samples, rate, subtype="PCM_16")


def synth(model_dir, text, path):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            subprocess.run([sys.executable, "-I", __file__, "--worker", model_dir, text, str(path)],
                           check=True, timeout=TIMEOUT)
            with wave.open(str(path)) as w:
                if w.getnframes() > 0:
                    return
            last = "empty wav"
        except (subprocess.SubprocessError, wave.Error, OSError) as e:
            last = e
        pathlib.Path(path).unlink(missing_ok=True)
        print(f"  retry {attempt}/{RETRIES}: {last}", file=sys.stderr)
    raise SystemExit(f"chunk failed after {RETRIES} tries: {text[:60]!r} ({last})")


def join_wavs(items, out):
    """items: [(wav_path, pause_seconds)]. Writes one 16-bit mono wav."""
    with wave.open(str(items[0][0])) as first:
        params = first.getparams()
    with wave.open(str(out), "wb") as dst:
        dst.setparams(params)
        for path, pause in items:
            with wave.open(str(path)) as src:
                if src.getparams()[:3] != params[:3]:
                    raise SystemExit("chunk format mismatch")
                dst.writeframes(src.readframes(src.getnframes()))
            dst.writeframes(b"\x00\x00" * int(params.framerate * pause))


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--worker":
        return worker(*sys.argv[2:5])
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--model-dir", default=os.environ.get("KOKORO_DIR", "."))
    ap.add_argument("--bitrate", default="24k", help="Opus bitrate, 24k to 28k")
    ap.add_argument("--dry-run", action="store_true", help="print the narration text and chunk count only")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        sys.exit("bad slug")
    src = ROOT / "content" / "posts" / f"{args.slug}.html"
    parts = chunks(src.read_text(encoding="utf-8"))
    words = sum(len(t.split()) for t, _ in parts)
    print(f"{args.slug}: {len(parts)} chunks, {words} words, longest chunk {max(len(t) for t, _ in parts)} chars")
    if args.dry_run:
        for t, p in parts:
            print(f"[{p}s] {t}")
        return
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not (pathlib.Path(args.model_dir) / f).is_file():
            sys.exit(f"missing {f} in {args.model_dir}; see the setup notes at the top of this file")
    dest = ROOT / "audio" / f"{args.slug}.opus"
    dest.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        items = []
        for i, (text, pause) in enumerate(parts, 1):
            wav = pathlib.Path(tmp) / f"{i:04d}.wav"
            synth(args.model_dir, text, wav)
            items.append((wav, pause))
            print(f"  {i}/{len(parts)}", flush=True)
        joined = pathlib.Path(tmp) / "all.wav"
        join_wavs(items, joined)
        part = pathlib.Path(tmp) / "out.opus"  # never leave a half-written file in audio/
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(joined),
                        "-ac", "1", "-c:a", "libopus", "-b:a", args.bitrate, "-application", "voip",
                        "-vbr", "on", "-map_metadata", "-1", str(part)], check=True)
        dest.write_bytes(part.read_bytes())
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dest)],
                           capture_output=True, text=True, check=True)
    secs = float(probe.stdout)
    wpm = words / (secs / 60)
    print(f"wrote {dest.relative_to(ROOT)}: {secs / 60:.1f} min, {dest.stat().st_size / 1e6:.2f} MB, {wpm:.0f} words/min")
    if not 110 <= wpm <= 190:
        sys.exit("words per minute is outside 110 to 190: listen closely, something may be missing or garbled")


if __name__ == "__main__":
    main()
