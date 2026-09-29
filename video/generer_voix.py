"""Synthesise the French voice-over, one clip per caption.

    PIPER_BIN=/chemin/piper PIPER_MODEL=/chemin/fr-siwis-medium.onnx python3 video/generer_voix.py

Writes video/build/voix/<segment>-<n>.wav and video/build/voix/manifeste.json
({segment: [{"texte", "fichier", "duree"}]}). Offline: uses Piper TTS.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import wave
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "build" / "voix"

# how the words are written for the ear, not the eye
SAY = [
    (r"\bIBM\b", "I.B.M."), (r"Entra ID", "Entra aï-di"), (r"\bMCP\b", "M.C.P."), (r"\bOPA\b", "O.P.A."),
    (r"\bAPI\b", "A.P.I."), (r"\bSIEM\b", "S.I.E.M."), (r"RFC 8693", "R.F.C. quatre-vingt-six, quatre-vingt-treize"),
    (r"\bJira\b", "Djira"), (r"GitLab", "Guitlabe"), (r"Databricks", "Data-brix"), (r"\bVault\b", "Vôlte"),
    (r"SPIFFE", "Spiffy"), (r"Antenna", "Anténa"), (r"«\s*", ""), (r"\s*»", ""),
]


def ear(text: str) -> str:
    for pat, rep in SAY:
        text = re.sub(pat, rep, text)
    return text


def main():
    piper = os.environ.get("PIPER_BIN", "piper")
    own = os.environ.get("VOIX_PERSO") == "1"   # keep WAVs you recorded yourself, only re-measure them
    model = None if own else os.environ["PIPER_MODEL"]
    OUT.mkdir(parents=True, exist_ok=True)
    script = json.loads((HERE / "narration.json").read_text(encoding="utf-8"))
    manifest = {}
    for seg, lines in script.items():
        if seg.startswith("_"):
            continue
        manifest[seg] = []
        for i, line in enumerate(lines):
            wav = OUT / f"{seg}-{i}.wav"
            if not own:
                subprocess.run([piper, "--model", model, "--output_file", str(wav), "--length_scale", "1.02",
                                "--sentence_silence", "0.25"],
                               input=ear(line).encode(), check=True, capture_output=True)
            with wave.open(str(wav)) as w:
                dur = w.getnframes() / w.getframerate()
            manifest[seg].append({"texte": line, "fichier": str(wav), "duree": round(dur, 3)})
    (OUT / "manifeste.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(c["duree"] for s in manifest.values() for c in s)
    print(f"{sum(len(s) for s in manifest.values())} clips, {total / 60:.1f} min de narration")


if __name__ == "__main__":
    main()
