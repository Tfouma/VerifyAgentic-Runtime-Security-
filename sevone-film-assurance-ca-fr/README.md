# Quand l'IA modifie le réseau, qui vérifie le résultat ? (version française)

The French version of the Canada–U.S. architecture edition (`../sevone-film-assurance-ca/`).
It runs 11:06. All on-screen text and the narration are in French, written for a Québec
audience: *infonuagique*, *billet* for ticket, and French number formatting (98,4 %, 09 h 24).
Configuration snippets and CLI output stay in English, as the real tools display them.

| File | Voice |
|------|-------|
| `sevone-assurance-fr-voix-femme.mp4` | **Woman's voice**: Kokoro-82M `ff_siwis` (model Apache-2.0; trained on the SIWIS corpus, CC-BY 4.0) |
| `sevone-assurance-fr-voix-homme.mp4` | **Man's voice**: Piper `fr_FR-upmc-medium`, speaker "pierre" (UPMC corpus, CC-BY-SA 4.0) |

Both files share the same video and include a French subtitle track you can switch on in the
player. Everything is a simulated scenario, and both narrations are synthetic voices.

## Rebuild it

```bash
python3 translate_fr.py
```

```bash
python3 build_film.py ../sevone-film-part2/film.html
```

```bash
python3 translate_fr.py --page
```

```bash
python3 narration_fr.py --engine kokoro --voice ff_siwis --model /path/to/kokoro --tag femme --inject
```

```bash
python3 narration_fr.py --engine piper --voice /path/to/fr_FR-upmc-medium.onnx --speaker 1 --tag homme
```

To mix a voice: copy `narration_<tag>.wav` and `narration_<tag>.json` to `narration.wav` and
`narration.json`, run `python3 soundtrack.py`, then mux the soundtrack with `video-fr.mp4` using
ffmpeg.

`narration_fr.py` also supports Chatterbox Multilingual (MIT licence, more natural, and it adds
an invisible AI watermark): `--engine chatterbox --ref <reference.wav>`. On a CPU it takes about
6 minutes per line, so use a GPU for a full narration.

## Credits

- **SIWIS French Speech Synthesis Database:** CC-BY 4.0.
- **UPMC "pierre" corpus (MaryTTS):** CC-BY-SA 4.0.
- **Kokoro-82M:** Apache-2.0.
