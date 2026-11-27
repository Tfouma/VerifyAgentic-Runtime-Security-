# Agentic Breach Demo — IBM Verify Identity Protection + Agentic Runtime Security

A workshop kit and simulation for showing clients how runtime identity controls stop a
compromised AI agent from exposing customer data and diverting funds.

**Everything here is fictional and simulated.** The bank, customers, accounts and balances
exist only in memory. Nothing touches a real system. The "controls on" mode models the
enforcement pattern of a runtime identity layer for AI agents. It is an independent
illustration, not IBM software.

## What's inside

| Path | What it is |
|------|------------|
| `docs/WORKSHOP_PLAN.md` | **Start here.** How many agents you need, which environment to use, the video storyboard, the 90-minute agenda, the talk track, discovery questions, objection handling and the call to action |
| `demo/dashboard.html` | The Breach Console: an interactive visual for the room and the recording |
| `demo/attack_map.html` | Lateral Movement Map: architecture view of each step, including the request chain across agents and the background checks that run on every call |
| `demo/fraud_ring.html` | **Fraud Ring Live**: four attacker crews go after money, personal data, card numbers and phone numbers at a fictional bank and mobile operator, all at once. Flip the controls or pull the kill switch mid-attack. In English or Canadian French (EN/FR switch, or `#fr` in the link) |
| `demo/agentic_runtime_architecture.html` | **Agentic Runtime Security, Step by Step**: the bank's reference architecture, redrawn from the reference slide, with a walkthrough of one request (sign-in, chat, tool call, agent token, token exchange, per-action token, the Vault decision, the two-minute database user), the activity feed, the three kill switches and IBM Verify Identity Protection. In English or Canadian French (EN/FR switch, or `#fr` in the link) |
| `demo/identity_explained.html` | **Identity Attacks, Explained**: a presenter's explainer in eleven scenes. How people and AI agents authenticate, the protocols and standards behind it, best practices, fraud and non-compliance, lateral movement, ISPM and ITDR. In English or Canadian French |
| `demo/film/the-agent-that-went-rogue.mp4` | **The demo film** (about 5 minutes): both runs in the Breach Console plus Lateral Movement Map scenes, with captions tagged to three agent-governance objectives (1080p, no audio) |
| `demo/film/the-agent-that-went-rogue-narrated.mp4` | The same film with a narrated sound track, paced so each line finishes before the next scene (1080p, AAC audio) |
| `demo/film/record_film.js` | Re-records the film from the two pages |
| `demo/film/narrate.py` | Speaks the narration locally with an open-weight text-to-speech model (Kyutai's Pocket TTS, or Kokoro) and mixes it onto one track |
| `demo/film/fraud-ring-live.mp4` | **Fraud Ring Live, the film** (narrated): the controls-off run, the replay with the controls on and the kill switch, and the six checks that stopped the crews |
| `demo/film/fraud-ring-live-fr.mp4` | The same film in Canadian French: French interface, captions, title cards and narration |
| `demo/film/record_fraud_ring.js` | Re-records the Fraud Ring Live film from `demo/fraud_ring.html`, in English or French |
| `demo/film/identity-attacks-explained.mp4` | **The teaching film** (13 minutes, narrated, with chapter marks): the explainer scenes and two Fraud Ring Live runs, from sign-in flows to ISPM and ITDR |
| `demo/film/identity-attacks-explained-fr.mp4` | The same film in Canadian French |
| `demo/film/record_identity_explained.js` | Re-records the teaching film, in English or French |
| `demo/film/agentic-runtime-security-step-by-step.mp4` | **The architecture film** (narrated, with chapter marks): the reference architecture explained step by step |
| `demo/film/agentic-runtime-security-step-by-step-fr.mp4` | The same film in Canadian French, with the diagram, panels and narration in French |
| `demo/film/record_runtime_architecture.js` | Re-records the architecture film, in English or French |
| `demo/film/lib.js` | Stage, camera, captions, narration timing and encoding shared by both film scripts |
| `demo/run.py` | Terminal narrator that prints the attack with controls OFF, then ON |
| `demo/bank.py` | In-memory mock bank |
| `demo/guardrail.py` | Simulated runtime control layer (agent identity, delegated mandate, per-action policy, quarantine) |
| `demo/agents.py` | The three scripted agents |
| `demo/scenario.py` | Scenario engine used by the CLI and the tests |

## Run it

Needs Python 3.9+. No dependencies.

```bash
python3 -m demo.run                # narrated terminal walkthrough
python3 -m unittest discover tests # verify the OFF/ON outcomes
```

For the explainer, open `demo/identity_explained.html` and step through it with the arrow keys
or the Next and Back buttons. **EN / FR** switches the language. The reference architecture
walkthrough, `demo/agentic_runtime_architecture.html`, works the same way.

For the dashboard, open `demo/dashboard.html` in a browser. Choose **Controls off** or
**Controls on**, then click **Run attack**. To explain what happens behind each step,
open `demo/attack_map.html` and step through it or click **Play chain**. For the live
version with a bank and a mobile operator, open `demo/fraud_ring.html`, press **Start attack**,
and switch the controls on whenever you like.

To re-record the film after changing either page, run `node demo/film/record_film.js`. It
needs Node 18+, Playwright with Chromium, and ffmpeg, and takes about seven minutes.
`FILM_CLIENT=Name` puts a client's name on the objective tags. Keep client-named cuts out
of this repository.

### Narration

Every narrated film is spoken by Kyutai's
[Pocket TTS](https://huggingface.co/kyutai/pocket-tts-without-voice-cloning), which runs on
a CPU and sounds far more natural than the first takes. In a Python 3.10+ environment, run
`pip install pocket-tts soundfile`, then point the film scripts at it:

```bash
export FILM_TTS=pocket FILM_PYTHON=/path/to/venv/bin/python
# English: the teaching film, the narrated Agent That Went Rogue, and Fraud Ring Live
FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 node demo/film/record_identity_explained.js
FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 node demo/film/record_film.js demo/film/the-agent-that-went-rogue-narrated.mp4
FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 node demo/film/record_fraud_ring.js
FILM_TTS_LANGUAGE=english FILM_VOICE=alba FILM_TTS_MAX_PAUSE=0.5 node demo/film/record_runtime_architecture.js
# Canadian French
FILM_LANG=fr FILM_TTS_LANGUAGE=french_24l FILM_VOICE=estelle node demo/film/record_identity_explained.js
FILM_LANG=fr FILM_TTS_LANGUAGE=french_24l FILM_VOICE=estelle node demo/film/record_fraud_ring.js
FILM_LANG=fr FILM_TTS_LANGUAGE=french_24l FILM_VOICE=estelle node demo/film/record_runtime_architecture.js
```

The model and voices download from Hugging Face the first time. `FILM_TTS_CACHE=/some/folder`
keeps every spoken line, so a re-render only speaks the lines you changed, and
`FILM_TTS_MAX_PAUSE=0.5` shortens long silences between sentences. The teaching films were
encoded with `FILM_CRF=22`, which keeps each file under 50 MB. Without `FILM_VOICE`, a film
runs with captions only.

The narration runs on your machine, so the script text never goes to an outside service.
`narrate.py` also still speaks with [Kokoro](https://github.com/thewh1teagle/kokoro-onnx)
(`FILM_TTS=kokoro`, the default, with `KOKORO_MODEL`, `KOKORO_VOICES` and a voice such as
`af_heart`); see its header for the setup.

## The story in one line

Three agents run the same attack twice. With controls **off**, 5 customer records are
exposed and **$430,000** moves to an account no customer asked to fund. With controls
**on**, every step is blocked and **$0** moves.

## Credits

The narration is spoken by [Pocket TTS](https://huggingface.co/kyutai/pocket-tts-without-voice-cloning)
from Kyutai (weights under CC BY 4.0). The English voice, `alba`, is voice actor Alba MacKenna's,
under CC BY 4.0. The French voice, `estelle`, is a Kyutai recording under CC0. See
[kyutai/tts-voices](https://huggingface.co/kyutai/tts-voices) for both.
