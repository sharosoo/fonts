# Nerd Font patching + web icon handling

## Patch environment
- `font-patcher` needs FontForge's Python module; the host has none. `scripts/lib/nerd.py` runs it in podman with `ghcr.io/nicoverbruggen/fntbld-oci:latest` (FontForge + fonttools), mounting the unzipped `FontPatcher.zip` (version and sha256 pinned in `font.toml`) read-only plus an output dir:
  `podman run --rm -v PATCHER:/patcher:ro -v IN:/in:ro -v OUT:/out IMAGE python3 /patcher/font-patcher --complete --quiet --no-progressbars [flags] -out /out /in/font.ttf`
- `nerd.py` runs the patch jobs from a thread pool.
- The patcher renames Reserved-Font-Name families itself (D2Coding → D2Koding) and builds names like `D2KodingLigature Nerd Font Mono`.

## `--mono` breaks CJK monospace fonts
- `--mono` forces every glyph, including existing ones, to one cell. D2Coding has Latin 500 and Hangul 1000; with `--mono` the Hangul advance drops to 500 while outlines stay 1000 wide.
- Use `--single-width-glyphs` for the terminal variant (only added icons are squeezed to one cell), then restore `post.isFixedPitch = 1` and `OS/2.panose.bProportion = 9`. Non-mono variants are expected to be non-fixed-pitch.
- `scripts/qa_nerd.py` checks after each patch: advances of `A` and `i` and a Hangul syllable; representative icon code points (Powerline E0B0, Seti E5FA, Devicons E700, Codicons EA60, Font Awesome F000, Material F0001, Octicons F400); a U+E700 icon bounding-box width of at most 520 units in Mono builds (it also reports `i` and icon advances); and `calt`/`liga` present only in the ligature build.

## Upstream facts
- D2Coding ships plain and `ligature` builds (Regular + Bold, TTF + TTC); the ligature build only adds `aalt/calt/liga`. It already has ~1,000 PUA glyphs (partial Powerline) but none of Seti, Devicons, Codicons, Font Awesome, Material, Octicons.
- Patched fonts are OFL; each icon set keeps its own license (see the Nerd Fonts license audit). Ship `LICENSE-nerd-fonts.txt` and point to the audit in `CREDITS.md`.

## Web fonts for a coding font
- Ship the ligature build only; plain text via CSS `font-variant-ligatures: none`.
- Main woff2s exclude the PUA (U+E000-F8FF). Icons come from the patched Mono Regular, split into a BMP file (U+E000-F8FF) and a Material file (U+F0000-FFFFD), each declared with `unicode-range` for weights 400 and 700 (same file). Pages without icons never download them.
- Rename the family (`graft.set_names`) before subsetting so web files respect the Reserved Font Name.
- Browser check: `canvas.measureText` at 16 px should give A = 8, i = 8, Hangul = 16, icon = 8.
