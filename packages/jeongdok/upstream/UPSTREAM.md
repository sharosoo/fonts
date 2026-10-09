# Upstream sources

Files under `upstream/` are unmodified copies; `font.toml` points at them.

## Libron (Latin)

- Source: https://github.com/nicoverbruggen/libron (Nico Verbruggen), OFL-1.1
- Version: v0.24, release `Libron.zip` (static TTF, 4 styles)
- Lineage: Newsreader (Production Type) → Readerly → Libron
- Reserved Font Name: **Libron**; Jeongdok is a modified version and is renamed.
- License text: `libron/OFL.txt` (from the Libron repository)

| File | SHA-256 |
|---|---|
| Libron-Regular.ttf | f5aa188902505f0f331124d1ed73d35e692500bb2a23f33ee6f114eef7d64314 |
| Libron-Italic.ttf | 6250447a37ca8d7c07682eddbaeeb47248e27c7b1c740c27911ed057230a944c |
| Libron-Bold.ttf | b54868b7fc86161d5776229315f3c1e52c22a6c739df970eae5d8bac1e31c1b6 |
| Libron-BoldItalic.ttf | e28056aeafaf31814e5efca25a4051d7606b816505d86900136a83f2f818b06c |

## RIDIBatang (Hangul)

- Original: RIDI Corporation / Sandoll Inc., OFL-1.1, https://ridicorp.com/ridibatang/. RIDIBatang is a registered trademark of RIDI Corporation; the name must not be used for derivatives.
- File used: `ridibatang/RIDIBatang-5.otf` (`fonts/RIDIBatang-5.otf`, releases v1.1.0/v1.2.0) from https://github.com/mcnorton/ridibatang-9.
- Community build caveat: Hangul advance widths are reduced by 5% (outlines unchanged), so glyph advances already include -5% tracking before `track` in `font.toml` applies.
- SHA-256: `9c55095e289ffac0a37af6a98f3d0d039d54d19c60360cd17ae5a54fb74c443d`
- The repository ships no LICENSE file; RIDI states the font is OFL and may be modified and redistributed. The OFL text and the RIDI/Sandoll copyright notice are in `OFL.txt` and every font file.
- If replaced by the original `RIDIBatang.otf`, set `track = 0.95` in `font.toml` to keep the same spacing.
