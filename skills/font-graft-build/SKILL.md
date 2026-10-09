---
name: font-graft-build
description: "Use when building, patching or packaging Korean OFL fonts in the fonts monorepo: Hangul grafting, Nerd Font patching, Kobo/CrossPoint/web builds, licensing and name-table rules."
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fonts, hangul, ofl, nerd-fonts, kobo, crosspoint, webfont, uv]
    category: creative
    related_skills: [typography-setup]
---

# Font graft + packaging

Repository: `~/workspaces/sharosoo/fonts`. Paths below are relative to that checkout.

Read `scripts/lib/graft.py`, `targets.py`, `nerd.py`, `fetch.py` and `packages/*/font.toml` before re-deriving anything. Adding a package: `docs/ADDING_A_PACKAGE.md`.

References: `references/nerd-patch.md` (Nerd patching, web icon split), `references/korean-font-candidates.md` (donor notes, sans metrics).

## Repo conventions
- One monorepo, `packages/<name>/`. `font.toml` has `kind = "graft" | "nerd-patch"`; `scripts/build.py` dispatches on it. `targets` limits builds (a heading face skips `kf`/`cpfont`).
- uv project (`pyproject.toml`, `uv.lock`, `.python-version`): `uv sync`, then `uv run scripts/build.py|qa.py|release.py <pkg>`. No hand-made venvs or requirements.txt. Code must run on the declared minimum Python (no nested same-type quotes in f-strings).
- `build.py` sets `SOURCE_DATE_EPOCH`, so `head.modified` is fixed and two builds give byte-identical woff2. Hash `dist/web` after two builds to confirm.
- E-reader/desktop fonts ship as GitHub Release assets (`dist/eink` is gitignored). Web fonts are committed under `dist/web` and served by jsDelivr from tag `<pkg>-v<ver>`.
- Upstream sources are pinned by URL + sha256 (`upstream/UPSTREAM.md`). Small OFL files are committed; large ones use `[[fetch]]` (plain file or zip `member`, optional `member_sha256`). Prefer the foundry's own download (Maru Buri: NAVER zip).
- `font.toml` knobs: `[family] slug` (CSS/file names without spaces), `ps_name` (no spaces; names release zips), `[qa] banned` (upstream names that must not survive in the name table), `[hangul.files]` (donor per style), `[latin.variable]` + `[latin.axes]` (variable Latin master instantiated per style).
- Commit locally; push, tag and publish only on explicit request.

## Licensing
- Modified fonts with a declared Reserved Font Name (see the upstream `OFL.txt`; Libron, D2Coding) must be renamed unless the rights holder grants written permission. Respect upstream trademarks separately (Newsreader, RIDIBatang in name ID 7). Credit upstream in `OFL.txt` / `CREDITS.md`.
- OFL counts patching, subsetting and woff2 conversion as modification, so a declared Reserved Font Name must not survive in any such file.
- Check the upstream license text before adopting any donor; do not base on fonts that forbid modification.
- Community re-uploads may lack a LICENSE (`ridibatang-9`): record the gap in `UPSTREAM.md`; prefer the original distribution before a public release.
- Run `scripts/qa.py <pkg>` after every build; for graft packages it fails on upstream names left in the name table.

## Graft pipeline (`kind = "graft"`)
1. **Variable Latin masters** (Newsreader): `fontTools.varLib.instancer` (e.g. opsz=72), then `removeOverlaps` (variable masters keep overlapping contours that Kobo and older rasterizers dislike). Drop `STAT/fvar/avar/gvar/HVAR/MVAR/VVAR`.
2. **Hangul outlines**: glyphSet → `TransformPen` → `Cu2QuPen(reverse_direction=is_cff)` → `TTGlyphPen`. After scaling, centre each glyph in its advance.
3. **Weight**: if the donor lacks the weight, offset outlines with skia-pathops (`stroke` + `convertConicsToQuads` + `op UNION`; draw with `reverse_direction=False`). Tune the offset so the Hangul/Latin ink ratio matches Regular. A donor with real weights (Maru Buri Bold) needs no offset.
4. **Hinting**: drop `fpgm/prep/cvt`, clear glyph programs, zero the `maxp` instruction fields.
5. **Metadata**: set OS/2 Hangul unicode/codepage bits; rewrite name IDs 0-6, 13, 14, 16-18; drop IDs 7 and 25 (25 is the variations PS prefix and leaks the upstream name). Do not trust the donor's style fields: pass the style explicitly and set `fsSelection` (italic bit 0, bold bit 5, regular bit 6), `head.macStyle`, `usWeightClass`. Variable instances keep "Regular". PS name has no spaces.

## Alignment
- Scale and vertical shift (`dy`) are chosen by eye: render guide-line sheets (baseline / x-height / cap height) for several values. Ink centroid and face centre only suggest candidates.
- RIDIBatang's Hangul centre sits ~0.09 em lower than the Source Han convention; against Libron/Newsreader use `scale = 0.94`, `dy = +0.09`. Both packages share these values; do not re-tune an approved alignment for unrelated reasons.
- "Hangul looks too small" is fixed by `scale` (and `track`), not weight. Weight only changes colour.
- Compare 3-4 donors on one sheet at ~76 px with identical text. Vision models cannot judge typographic colour; use numbers for loops and eyes for the final call.

## Measurement
- PIL `ImageDraw.text` defaults to anchor `la`. Measure ink with anchor `ls` on a tall canvas, or glyphs clip and ratios come out wrong (`scripts/qa.py` does this).

## Targets
- **Kobo (`kf`)**: `kobofix.py --preset kf` (v0.10, fetched by `scripts/fetch_tools.py`). Needs the `ots-sanitize` binary, which `opentype-sanitizer` ships inside its package (`ots/ots-sanitize`); `targets.py` puts it on PATH.
- **CrossPoint (`cpfont`)**: `fontconvert_sdcard.py --intervals reading,hangul --sizes 12,14,16,18`; `font-line percent 35`, then copy hhea ascent/descent/lineGap into OS/2 typo metrics. Full Hangul makes large files per size. Unverified on device.
- **Web**: per style, woff2 full, KS X 1001 subset (Hangul filtered by EUC-KR decode of 0xB0A1-0xC8FE), and dynamic subset using the Noto Serif KR `unicode-range` slice CSS (`tools/slices/notoserifkr.css`, from Google Fonts with a Chrome UA). Characters outside every slice go into one extra leftover slice. Subsetting runs in a `ProcessPoolExecutor`.

## Nerd patching (`kind = "nerd-patch"`)
- Run `font-patcher` in the FontForge container (`ghcr.io/nicoverbruggen/fntbld-oci`, podman). Details: `references/nerd-patch.md`.
- Never pass `--mono` to a font with 2-cell Hangul: it shrinks the Hangul advance 1000 → 500 and Korean text overlaps. Use `--single-width-glyphs`, then restore `post.isFixedPitch = 1` and PANOSE `bProportion = 9`.
- Web: ligature build only; PUA split into BMP and Material (U+F0000+) symbol fonts joined by `unicode-range`.
