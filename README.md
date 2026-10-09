# sharosoo/fonts

Fonts derived from OFL typefaces, built for E Ink readers, desktop and the web.

| Font | Use | Made from | Version |
|---|---|---|---|
| [Jeongdok](packages/jeongdok) | Body text, long-form reading, E Ink | Libron (Latin) + RIDIBatang (Hangul) | 0.1.0 |
| [Jeongdok Display](packages/jeongdok-display) | Headings and branding, 28px and up | Newsreader opsz 72 (Latin) + Maru Buri (Hangul) | 0.1.0 |
| [D2Koding](packages/d2koding) | Code and terminals | D2Coding + Nerd Fonts, ligature and plain builds | 1.4.0 |

All three in use: [specimen PDF](docs/specimen/typography-specimen.pdf).

## How it is managed

- One directory per font, `packages/<name>/`. Build settings live in `font.toml`; source fonts sit in `upstream/` with origin and SHA-256 in `UPSTREAM.md`.
- Outputs: desktop TTF, Kobo (`kf`), CrossPoint (`cpfont`) and web (woff2 + CSS split by `unicode-range`). Jeongdok Display ships TTF and web only.
- Releases: pushing a tag `<name>-v<version>` (e.g. `jeongdok-v0.1.0`) makes GitHub Actions build the font and attach the zips to GitHub Releases. Each font is versioned and released on its own.
- Web fonts are committed under `packages/<name>/dist/web` and served by jsDelivr from the tag:

  ```
  https://cdn.jsdelivr.net/gh/sharosoo/fonts@<name>-v<version>/packages/<name>/dist/web/static/<name>-dynamic-subset.css
  ```

## Build

Requires [uv](https://docs.astral.sh/uv/); D2Koding also needs podman.

```bash
uv sync
uv run scripts/fetch_tools.py      # Kobo / CrossPoint converters
uv run scripts/build.py jeongdok   # --only ttf,kf,cpfont,web
uv run scripts/qa.py jeongdok
```

Adding a font: [docs/ADDING_A_PACKAGE.md](docs/ADDING_A_PACKAGE.md). Recommended pairing and CSS: [docs/TYPOGRAPHY_SETUP.md](docs/TYPOGRAPHY_SETUP.md).

## License

Fonts: SIL OFL 1.1 (`OFL.txt` in each package). Build scripts: MIT.
