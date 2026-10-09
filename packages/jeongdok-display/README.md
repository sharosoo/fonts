# Jeongdok Display

Heading and brand cut of [Jeongdok](../jeongdok): Newsreader at its Display optical size (opsz 72) plus Maru Buri Hangul. Use Jeongdok for body text.

## Downloads

| Target | File | Where |
|---|---|---|
| Desktop | `JeongdokDisplay-<version>-desktop.zip` (4 TTF) | GitHub Releases |
| Web | CDN below, or `JeongdokDisplay-<version>-web.zip` | cdn.sharosoo.com / Releases |

No Kobo or CrossPoint builds.

## Web

```html
<link rel="stylesheet"
  href="https://cdn.sharosoo.com/fonts/jeongdok-display/v0.1.0/jeongdok-display-dynamic-subset.css">
<style> h1, h2 { font-family: 'Jeongdok Display', 'Jeongdok', serif; } </style>
```

The URL is available once `jeongdok-display-v0.1.0` is released; the `v0.1.0` path is immutable.

| CSS | Content |
|---|---|
| `jeongdok-display-dynamic-subset.css` | 94 unicode-range slices per style |
| `jeongdok-display-subset.css` | Latin + KS X 1001 Hangul (2,350 syllables) |
| `jeongdok-display.css` | All 11,172 Hangul syllables |

## Spec

| | |
|---|---|
| Styles | Regular, Italic, Bold, BoldItalic |
| Intended size | about 28 px and up |

## Build

```bash
uv run scripts/build.py jeongdok-display
uv run scripts/qa.py jeongdok-display
```

Demo: `python3 -m http.server 8791` at the repo root, then open `/packages/jeongdok-display/demo/`.

Rationale: [docs/DESIGN.md](docs/DESIGN.md). License: SIL OFL 1.1.
