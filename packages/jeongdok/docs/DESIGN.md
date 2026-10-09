# Jeongdok design

Libron (Latin) + RIDIBatang (Hangul), tuned so mixed text reads as one face on E Ink.

## Build

1. Libron's four static TTFs are used unchanged.
2. From RIDIBatang, import Hangul syllables, compatibility jamo, CJK punctuation and fullwidth forms (CFF to quadratic via `cu2qu`), then scale and shift:
   - `scale = 0.94` (Hangul em relative to Libron em)
   - `dy = 0.09` em (baseline shift)
   - `track = 1.0` (on top of the upstream -5% advance)
3. Bold and BoldItalic: RIDIBatang has one weight, so outlines are offset by 0.0105 em per side (skia-pathops stroke + union).
4. Italic styles reuse the upright Hangul.
5. Drop TrueType bytecode (the Kobo KF pipeline strips it too), rename, write OFL metadata.

## Values

| Value | Reason |
|---|---|
| `scale` 0.94 | 1.00 looked too large next to Libron's x-height (0.531 em); 0.94 chosen over 0.90 / 0.86 by eye |
| `dy` 0.09 | RIDIBatang's Hangul centre sits ~0.09 em lower than the Source Han/Noto convention (0.375 vs 0.288 em after scaling); +0.09 puts the Hangul bottom edge on the Latin baseline |
| embolden 0.0105 | Makes Bold's Hangul/Latin ink ratio match Regular (0.90 vs 0.89) |

`scale` and `dy` were set visually, not computed. Re-check on a device before changing them.

## Measurements

`scripts/qa.py` (FreeType, 100 px, ink per advance × em):

| Style | Hangul/Latin ink ratio |
|---|---|
| Regular | 0.89 |
| Italic | 0.94 |
| Bold | 0.90 |
| BoldItalic | 0.93 |

Libron Regular (em units): x-height 0.531, cap height 0.698, vertical stem 0.103, hairline/stem 0.72.

## Limits

- Only Hangul and punctuation are grafted; no hanja.
- No Hangul kerning (GPOS) or Hangul-specific OpenType features.
- Not verified on a physical Kobo or Xteink device.
- RIDIBatang is the community -5% tracking build, kept as-is (see `upstream/UPSTREAM.md`).
