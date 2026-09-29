"""Mix the voice-over onto the screen recording and export MP4 + SRT.

    FFMPEG=/chemin/ffmpeg python3 video/assembler.py

Reads video/build/brut.webm and video/build/chronologie.json, writes
video/demo-agent-gouverne.mp4 and video/demo-agent-gouverne.srt.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
BUILD = HERE / "build"
NAME = "demo-agent-gouverne"


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ff = os.environ.get("FFMPEG", "ffmpeg")
    clips = json.loads((BUILD / "chronologie.json").read_text(encoding="utf-8"))

    # one audio track: every clip delayed to the moment its caption appeared
    inputs, filters = [], []
    for i, c in enumerate(clips):
        inputs += ["-i", c["fichier"]]
        ms = int(c["debut"] * 1000)
        filters.append(f"[{i + 1}:a]adelay={ms}|{ms},aresample=48000[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(clips)))
    filters.append(f"{mix}amix=inputs={len(clips)}:normalize=0,volume=1.4,alimiter=limit=0.89:level=0[voix]")
    out = HERE / f"{NAME}.mp4"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(BUILD / "brut.webm"), *inputs,
                    "-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[voix]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-pix_fmt", "yuv420p", "-r", "25",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", str(out)], check=True)

    srt = []
    for i, c in enumerate(clips, 1):
        srt.append(f"{i}\n{ts(c['debut'])} --> {ts(c['debut'] + c['duree'])}\n{c['texte']}\n")
    (HERE / f"{NAME}.srt").write_text("\n".join(srt), encoding="utf-8")
    print(f"{out} ({out.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
