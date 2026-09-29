# Theresia (USA, NDS) Korean patch tooling

The ROM is never stored here. Provide your own dump (SHA-1 `55c846e3eacef50e89e54f226da782d9875f1622`).

    pip install ndspy pillow
    python3 tools/theresia/build_rom.py "Theresia (USA).nds" theresia_ko.nds

- `translations/theresia/ko.tsv`: Korean text keyed by SHA-1 of the source unit (English is re-derived from your ROM).
- `fonts/Galmuri11.ttf`: Hangul glyph source (SIL OFL 1.1, see `fonts/Galmuri-OFL.md`).
- Untranslated units keep their original English text, so partial builds are playable.
- `tr.py` is the translation workflow helper; `scriptio.py`/`lib.py` slice the `.adv`/`.txt` script pairs; `nftr.py` rebuilds the font.

Status: see `docs/theresia/initial-survey.md`. Runtime verification so far: boots and shows Hangul in the intro on headless DeSmuME.
