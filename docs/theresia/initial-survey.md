# Theresia (USA) NDS — initial survey (in progress)

Source ROM is not committed. Provided by the user via private link; kept only in session scratch.

## Input boundary
- Title `THERESIA`, game code `YJAE` (USA), maker `XS`, 64 MiB (67,108,864 bytes).
- SHA-1 `55c846e3eacef50e89e54f226da782d9875f1622` (supported revision fingerprint).
- ARM9 482,520 B, ARM7 159,192 B, 160 ARM9 overlays, no ARM7 overlays, banner 2,112 B (version to be checked before any banner change).
- NitroFS: 764 files, all under `data/`. Unchanged rebuild round trip: **not yet established** (required before editing).

## Text and asset map (facts vs. candidates)
| Item | Status | Notes |
|---|---|---|
| `data/script/**/*.txt.txt` (11 files) | fact | LZ10-compressed (header `10`), decompress to ~1.39 MB total; English text, `%W<n>` wait controls, Shift-JIS fullwidth space (`81 40`) used as indent. ~6,500 `%W`-delimited segments (lower bound, counts only segments split by `%W`). |
| `data/script/**/*.txt.adv`, `*.cls` | candidate | `.adv` is LZ10; holds per-line records (likely offsets/commands into the `.txt`). Consumer not yet established. `.cls` 1,424 B, not compressed. |
| `data/system.txt` | fact | 1,878 B plain text: UI/place labels (`B3F`, `Channel `, `Maze `, ...). |
| `data/a.NFTR` | candidate | LZ10 -> 6,208 B NFTR; too small to be a full CJK font. Which font path actually renders script text is **unresolved**. |
| `data/*pack.dat`, `bgdata.dat`, `spdata.dat` | unresolved | Graphics packs (`ncgpack.dat` 35.9 MB). Baked-in graphics text (menus, titles) not surveyed. |
| Movies (`*.mods`), sound, 3D models | out of scope until shown to contain text | Subtitles in movies not checked. |

## Proceed / risk table
| Risk | Next evidence |
|---|---|
| Text-to-consumer link (`.txt` vs `.adv` vs ARM9/overlay) unknown | Decode `.adv` records; find script-loader code in ARM9/overlays (load path of `*.txt.txt`). |
| Glyph path: 88 distinct byte values, effectively Latin-1/ASCII font, no Hangul | Locate the renderer and font (a.NFTR vs baked tiles vs ARM9 table); measure Hangul cell/glyph demand from a translated corpus. |
| Volume: ~1 MB raw English, thousands of lines | Establish exact segment denominator once `.adv` structure is decoded; plan tooling for batch translation + QA (hanpatch gates need an OpenAI-compatible endpoint). |
| Reinsertion: LZ10 files, size growth | Verify FAT/loader tolerance; Korean text is longer in bytes if 2-byte encoding is used. |
| Graphics text | Survey `ncgpack.dat`/`nscpack.dat` for baked English text (title, menus, item names). |
| Runtime verification in cloud (no display) | Check whether emucap's DeSmuME-fork adapter can run headless here; otherwise verify statically and request user runtime checks. |

## Human decisions needed (to be presented at convergence)
- Scope: full script (~1 MB) vs main scenes only; treatment of `sub/`, `opt/`, `opt2/` variants.
- Font/encoding approach and quality bar; translation source is the English text, target Korean.
