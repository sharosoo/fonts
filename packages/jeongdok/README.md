# Jeongdok

Body serif for E Ink reading of mixed Hangul and Latin text: [Libron](https://github.com/nicoverbruggen/libron) Latin plus RIDIBatang Hangul.

## Downloads

| Target | File | Where |
|---|---|---|
| Desktop, Kindle, other e-readers | `Jeongdok-<version>-desktop.zip` (4 TTF) | GitHub Releases |
| Kobo (kepub) | `Jeongdok-<version>-kobo.zip` (`KF_Jeongdok-*.ttf`) | GitHub Releases |
| Xteink X3/X4 (CrossPoint) | `Jeongdok-<version>-crosspoint.zip`; copy to `/fonts/Jeongdok/` on the SD card | GitHub Releases |
| Web | CDN below, or `Jeongdok-<version>-web.zip` | cdn.sharosoo.com / Releases |

## Web

```html
<link rel="stylesheet"
  href="https://cdn.sharosoo.com/fonts/jeongdok/v0.1.0/jeongdok-dynamic-subset.css">
<style> body { font-family: 'Jeongdok', serif; } </style>
```

The URL is available once `jeongdok-v0.1.0` is released; the `v0.1.0` path is immutable.

| CSS | Content |
|---|---|
| `jeongdok-dynamic-subset.css` | 94 unicode-range slices per style; only slices used by the page load |
| `jeongdok-subset.css` | Latin + KS X 1001 Hangul (2,350 syllables), one woff2 per style |
| `jeongdok.css` | All 11,172 Hangul syllables, one woff2 per style |

## Spec

| | |
|---|---|
| Styles | Regular, Italic, Bold, BoldItalic |
| Hangul | RIDIBatang (-5% tracking build); no hanja |
| CrossPoint sizes | 12, 14, 16, 18 (`.cpfont`, 6.6–13.4 MB each) |
| Status | 0.1.0 prototype; not verified on a physical device |

## Build

```bash
uv sync                               # repo root
uv run scripts/fetch_tools.py         # kobofix, CrossPoint converter
uv run scripts/build.py jeongdok      # ttf -> kf -> cpfont -> web
uv run scripts/qa.py jeongdok         # names, glyph counts, ink balance
```

Output: `dist/eink/{ttf,kf,cpfont}` (not committed; attached to Releases) and `dist/web/static` (not committed; uploaded to cdn.sharosoo.com on release).

Demo: `python3 -m http.server 8791` at the repo root, then open `/packages/jeongdok/demo/`.

## Files

- `font.toml`: build settings
- `upstream/UPSTREAM.md`: sources and hashes
- `docs/DESIGN.md`: design decisions and measurements
- `OFL.txt`, `CREDITS.md`: license and credits

License: SIL OFL 1.1.
