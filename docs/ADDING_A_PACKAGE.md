# Adding a font package

1. Create `packages/<name>/` by copying `packages/jeongdok/`. It needs `font.toml`, `VERSION`, `CHANGELOG.md`, `README.md`, `CREDITS.md`, `OFL.txt`, `package.json`, `upstream/` and `docs/DESIGN.md`.
2. Put upstream fonts in `upstream/`. Record source, version, SHA-256 and license in `upstream/UPSTREAM.md`. Do not commit large files: declare them as `[[fetch]]` entries in `font.toml` instead.
3. Do not use an upstream Reserved Font Name (declared in its `OFL.txt`, for example Libron, D2Coding) or an upstream trademark (for example Newsreader, RIDIBatang) in the font's names. List them in `CREDITS.md` and the `font.toml` copyright.
4. Write `font.toml` (keys below). Tune Hangul `scale` and `dy` by eye and record the reasoning in `docs/DESIGN.md`.
5. Build and check: `uv run scripts/build.py <name>`, then `uv run scripts/qa.py <name>`.
6. Release: make `VERSION` equal `[family] version` in `font.toml`, then `uv run scripts/release.py <name>`. It writes the zips and `SHA256SUMS` to `dist/release/` and prints the publish commands; `--publish` runs them (commit, tag `<name>-v<version>`, push, `gh release create`).

A package that is neither `graft` nor `nerd-patch` needs a new entry in `KINDS` in `scripts/build.py` (target order and build functions; graft targets live in `TARGETS` in `scripts/lib/targets.py`).

## font.toml keys

| Key | Meaning |
|---|---|
| `kind` | `"graft"` (default: Latin + Hangul) or `"nerd-patch"` (patched monospace) |
| `targets` | Select build targets. graft: `ttf`, `kf`, `cpfont`, `web`; nerd-patch: `nerd`, `web`. Release packaging always requires `ttf` + `web` for graft, or `nerd` + `web` for nerd-patch; `kf` and `cpfont` assets are conditional. Jeongdok Display uses `["ttf", "web"]` |
| `[family]` | `name`, `ps_name` (file prefix, `<ps_name>-<Style>.ttf`), `version`, `url`, `copyright` (name ID 0) |
| `[family] styles` | graft only: `Regular`, `Italic`, `Bold`, `BoldItalic`. Web needs `Regular`; `cpfont` needs all four |
| `[family] slug` | CSS file name base; defaults to the lower-cased `name`, so set it when the name contains a space |
| `[latin] pattern` | Static Latin files, with `{style}` placeholder |
| `[latin.variable]`, `[latin.axes]` | Variable Latin source (`roman`, `italic`) and per-style axis values; instances are built per style (see `jeongdok-display`) |
| `[hangul] file` | Hangul source used for every style |
| `[hangul.files]` | Per-style Hangul sources, when styles differ |
| `[hangul] scale`, `dy`, `track` | Hangul size relative to its source em, baseline shift in Latin em, advance multiplier |
| `[hangul] ranges` | Unicode ranges taken from the Hangul font |
| `[hangul.embolden]` | Per-style outline offset in em per side; 0 when the source has a real bold |
| `[[fetch]]` | Pinned download: `url`, `sha256`, `dest` (relative to the package). For a zip member add `member` and optional `member_sha256`; `sha256` is then the zip's |
| `[web] slices` | CSS file with `unicode-range` slices, relative to the repo root (`tools/slices/notoserifkr.css`) |
| `[cpfont]` | CrossPoint build: `sizes`, `line_percent`, `intervals` |
| `[qa] banned` | Strings that must not appear in the name table (copyright, ID 0, is exempt). Default: Libron, Readerly, Newsreader, RIDI, LibRidi |
| `[upstream]`, `[upstream.files]` | nerd-patch: pinned release `zip_url`, `zip_sha256`, and the file path of each member by key |
| `[nerd]`, `[nerd.variants]` | nerd-patch: `version`, `patcher_url`, `patcher_sha256`, container `image`; variants map a name to FontPatcher flags |
| `[web] regular`, `bold`, `symbols_from` | nerd-patch: upstream key used for each web weight, and the patched file the icon slices come from |

## QA checklist

For graft packages, `scripts/qa.py` reports name leaks, Hangul coverage and ink ratios; only name leaks fail the run, so check the other two yourself. Nerd-patch QA checks widths, icons and ligatures instead. The rest is manual.

- [ ] No upstream Reserved Font Name left in the name table (`name-leaks=[]`, ends with `OK`).
- [ ] All 11,172 Hangul syllables present (`hangul=11172/11172`).
- [ ] Hangul/Latin ink ratio 0.85–1.0 (`hangul/latin ink`).
- [ ] Latin and Hangul share a baseline (compare visually in the demo).
- [ ] Web slices cover every glyph; the build reports leftover characters, which become an extra slice.
- [ ] Renders correctly on the target device.

To regenerate the specimen PDF after building `jeongdok`, `jeongdok-display` and `d2koding`: `uv run scripts/specimen.py` (needs Chromium and network access for Google Fonts).
