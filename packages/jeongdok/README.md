# Jeongdok

Body serif for E Ink reading of mixed Hangul and Latin text: [Libron](https://github.com/nicoverbruggen/libron) Latin plus RIDIBatang Hangul.

## Downloads

| Target | File | Where |
|---|---|---|
| Desktop, Kindle, other e-readers | `Jeongdok-<version>-desktop.zip` (4 TTF) | GitHub Releases |
| Kobo (kepub) | `Jeongdok-<version>-kobo.zip` (`KF_Jeongdok-*.ttf`) | GitHub Releases |
| Xteink X3/X4 (CrossPoint) | `Jeongdok-<version>-crosspoint.zip`; copy to `/fonts/Jeongdok/` on the SD card | GitHub Releases |
| Web | CDN below, or `Jeongdok-<version>-web.zip` | jsDelivr / Releases |

## Web

```html
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/gh/sharosoo/fonts@jeongdok-v0.1.0/packages/jeongdok/dist/web/static/jeongdok-dynamic-subset.css">
<style> body { font-family: 'Jeongdok', serif; } </style>
```

Use `@main` instead of the tag until the tag exists.

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

Output: `dist/eink/{ttf,kf,cpfont}` (not committed; attached to Releases) and `dist/web/static` (committed; served by jsDelivr).

Demo: `python3 -m http.server 8791` at the repo root, then open `/packages/jeongdok/demo/`.

## Files

- `font.toml`: build settings
- `upstream/UPSTREAM.md`: sources and hashes
- `docs/DESIGN.md`: design decisions and measurements
- `OFL.txt`, `CREDITS.md`: license and credits

License: SIL OFL 1.1.
