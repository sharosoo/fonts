# Upstream sources

Not committed. `scripts/build.py` downloads them into `upstream/cache/` (gitignored) and verifies the hash.

| Source | Pin |
|---|---|
| D2Coding VER1.4.0 | `D2Coding-Ver1.4.0-20261003.zip`, sha256 `17e2da5e2879006eb725b87943f7988736ef8b6c9f8b84bc8e3bdbcb8dd46744` |
| Nerd Fonts FontPatcher v3.5.1 | sha256 `42bcb32145499a35732274c7fc48deb434ad0d2e0e118f98527c1479c6fa251a` |
| Patch container | `ghcr.io/nicoverbruggen/fntbld-oci:latest` (FontForge + Python bindings), run with podman |

- D2Coding ships plain and ligature builds, Regular and Bold, as TTF and TTC; only the TTFs are used.
- Upstream already contains ~1,000 private-use glyphs (partial Powerline); font-patcher adds the Nerd Fonts sets (Seti, Devicons, Codicons, Font Awesome, Material, Octicons, ...).
