# D2Koding

NAVER [D2Coding](https://github.com/naver/d2codingfont) patched with [Nerd Fonts](https://www.nerdfonts.com/) icons, with ligature and plain builds, for terminals, editors and web code blocks.

"D2Coding" is a Reserved Font Name, so modified files are named **D2Koding**, as Nerd Fonts does. See `CREDITS.md`.

## Downloads

| Target | File | Where |
|---|---|---|
| Terminals, editors | `D2Koding-<version>-nerd.zip`: `mono/` and `default/`, each with 4 TTF (2 families × Regular, Bold) | GitHub Releases |
| Web | CDN below, or `D2Koding-<version>-web.zip` | cdn.sharosoo.com / Releases |

## Families

| Family | Ligatures | Use |
|---|---|---|
| `D2Koding Nerd Font Mono` | no | Recommended for terminals. Icon 1 cell, Latin 1 cell, Hangul 2 cells |
| `D2KodingLigature Nerd Font Mono` | yes | Same, with `->`, `!=`, `>=` etc. |
| `D2Koding Nerd Font` | no | Icons may overhang the next cell (large prompt icons) |
| `D2KodingLigature Nerd Font` | yes | Same, with ligatures |

Terminal example: `font-family = D2KodingLigature Nerd Font Mono`. Hangul is 2 cells wide, as in D2Coding.

## Web

```html
<link rel="stylesheet"
  href="https://cdn.sharosoo.com/fonts/d2koding/v1.4.0/d2koding-dynamic-subset.css">
<style>
  pre, code { font-family: 'D2Koding', monospace; }
  .no-ligature { font-variant-ligatures: none; }   /* web files are the ligature build only */
</style>
```

The URL is available once `d2koding-v1.4.0` is released; the `v1.4.0` path is immutable.

| CSS | Content |
|---|---|
| `d2koding-dynamic-subset.css` | 125 text slices per weight, plus two on-demand icon fonts that load only when private-use characters appear: `NerdSymbols` (BMP, 4,264 characters, 539 KiB), `NerdSymbolsMaterial` (U+F0000+, 6,896 characters, 384 KiB) |
| `d2koding.css` | Full Regular and Bold woff2 |

## Build

```bash
uv run scripts/build.py d2koding   # download upstream, patch in podman, build web fonts
uv run scripts/qa.py d2koding
```

Requires podman (container with FontForge).

Demo: `python3 -m http.server 8791` at the repo root, then open `/packages/d2koding/demo/`.

Rationale: [docs/DESIGN.md](docs/DESIGN.md). License: SIL OFL 1.1; Nerd Fonts terms in `LICENSE-nerd-fonts.txt`.
