# Typography setup

How to combine the four fonts in a web page, document, or e-book. Visual examples: [specimen PDF](specimen/typography-specimen.pdf).

## Roles

| Role | Font | Source | Use for |
|---|---|---|---|
| Body | Jeongdok | this repo | Long-form text, articles, e-book body |
| Headings, branding | Jeongdok Display | this repo | Headings and taglines, 28px and up |
| UI, sans text | IBM Plex Sans KR | Google Fonts (OFL, used unmodified) | Buttons, labels, tables, forms, navigation |
| Code | D2Koding | this repo | Code blocks, terminals, logs |

- Use at most one font per role, and only these four, on a screen.
- Jeongdok Display has hairline strokes: never set it below 28px or use it for body text. It has two weights, 400 and 700.

## Loading web fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<link rel="stylesheet" href="https://cdn.sharosoo.com/fonts/jeongdok/v0.1.0/jeongdok-dynamic-subset.css">
<link rel="stylesheet" href="https://cdn.sharosoo.com/fonts/jeongdok-display/v0.1.0/jeongdok-display-dynamic-subset.css">
<link rel="stylesheet" href="https://cdn.sharosoo.com/fonts/d2koding/v1.4.0/d2koding-dynamic-subset.css">
```

- Each CSS is a dynamic subset: Hangul is split by `unicode-range`, so the browser downloads only the slices a page uses. `font-display: swap` is set.
- URLs have the form `https://cdn.sharosoo.com/fonts/<name>/v<version>/…` and are available once the tag `<name>-v<version>` is released. A version path is immutable.
- `'Noto Serif KR'` in `--font-serif` is a fallback that is used only if installed on the device; nothing here loads it.

## Tokens and base styles

```css
:root {
  --font-sans:    'IBM Plex Sans KR', system-ui, -apple-system, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
  --font-serif:   'Jeongdok', 'Noto Serif KR', serif;
  --font-display: 'Jeongdok Display', 'Jeongdok', serif;
  --font-mono:    'D2Koding', ui-monospace, 'SF Mono', Menlo, monospace;

  --fs-ui: 14px;  --fs-body: 18px;  --fs-h3: 22px;  --fs-h2: 28px;  --fs-h1: 48px;
}
body        { font: var(--fs-body)/1.75 var(--font-serif); }
.ui, button { font: 500 var(--fs-ui)/1.5 var(--font-sans); }
h1          { font: 700 var(--fs-h1)/1.2 var(--font-display); }
h2          { font: 700 var(--fs-h2)/1.2 var(--font-display); }
h3          { font: 700 var(--fs-h3)/1.3 var(--font-sans); }
code, pre   { font: 14px/1.5 var(--font-mono); }
```

The values are defaults; adjust by eye on the real screen.

## Body

- Default 18px with line-height 1.75; adjust within 16–20px and 1.7–1.8.
- Line length: about 28–38 Hangul or 55–75 Latin characters (`max-width: 36em`).
- Line breaking: `p { word-break: keep-all; overflow-wrap: break-word; text-wrap: pretty; }`. Korean normally breaks at word boundaries; an otherwise unbreakable word may break internally to prevent overflow.
- Keep default letter-spacing; if you tighten it, go no lower than -0.01em.
- Latin has an italic; Hangul does not. Emphasize Hangul with bold.

## Headings

Below 28px use the sans face for headings.

## UI and numerals

- Use `font-variant-numeric: tabular-nums` where digits must align vertically: tables, prices, counters.
- Use SVG for icons, not an icon font.

## Code

- D2Koding is fixed-width: 1 cell per Latin character, 2 per Hangul character, so Hangul comment columns stay aligned. Line-height 1.5.
- Ligatures are on by default; disable with `font-variant-ligatures: none`.
- Nerd icons (PUA range) are a separate file, downloaded only when such a character appears.
- For terminals, install a font from the `mono/` folder of `D2Koding-<version>-nerd.zip` on GitHub Releases: `D2Koding Nerd Font Mono`, or `D2KodingLigature Nerd Font Mono` for ligatures.

## E Ink

- Use Jeongdok for body text. Jeongdok Display has no Kobo or CrossPoint files.
- Kobo: `Jeongdok-<version>-kobo.zip`. CrossPoint: `Jeongdok-<version>-crosspoint.zip`; unzip and copy the `Jeongdok/` folder to `/fonts/Jeongdok/` on the SD card. The CrossPoint build includes sizes 12, 14, 16 and 18.
- Check size and weight on the device itself after any change.
