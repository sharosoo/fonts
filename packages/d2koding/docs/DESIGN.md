# D2Koding design

## `--single-width-glyphs`, not `--mono`

- Nerd Fonts `--mono` forces every glyph to one cell. D2Coding draws Hangul 1000 units wide (two 500 cells), so with `--mono` the advance of U+AC00 (a Hangul syllable) becomes 500 while the outline stays 1000 wide and Korean text overlaps.
- The Mono variant uses `--single-width-glyphs`: only added icons are squeezed to one cell. `post.isFixedPitch = 1` and PANOSE "monospaced" are then restored, as in the upstream font.
- Measured with `scripts/qa_nerd.py`: Mono variant has `A`/`i` 500, Hangul 1000, icons 500; Default variant has icons ~800 (overhang).

## Ligatures

- D2Coding ships a separate ligature build (`calt`, `liga`, `aalt` GSUB features). Nerd patching preserves them.
- The web package ships only the ligature build (a superset); `font-variant-ligatures: none` turns ligatures off.

## Web

- Main fonts exclude the private-use area. Icons come from two symbol-only fonts cut from the patched Mono Regular and linked by `unicode-range`.
- Slices reuse the Google Fonts Noto Serif KR unicode-range map.
- Checked in a browser: `A`/`i` 1 cell, Hangul 2 cells, icon 1 cell.

## Naming

Reserved Font Name "D2Coding": modified versions are renamed D2Koding. Under the OFL, subsetting and woff2 conversion count as modification, so web files carry the new name too.
