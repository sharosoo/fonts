# Jeongdok Display design

Heading and brand cut of [Jeongdok](../../jeongdok); same graft pipeline, different parts.

## Build

- Latin: Newsreader at `opsz` 72, `wght` 400 / 700; Italic from the italic master. Variable instances are de-overlapped with skia-pathops (`removeOverlaps`) and variation tables are dropped.
- Hangul: Maru Buri Regular / Bold. Real weights, so no outline offset. Italic styles reuse the upright Hangul.
- `scale = 0.94`, `dy = 0.09`: same as Jeongdok, so body and display baselines match. Re-check at large sizes with the demo guide lines.
- Targets: `ttf` and `web` only.
- For large sizes (about 28 px and up); use Jeongdok for body text.

## Why Maru Buri, not RIDIBatang

Newsreader Display has very thin hairlines (hairline/stem ≈ 0.22 at opsz 72). Compared at 76 px:

| Hangul | Result |
|---|---|
| RIDIBatang | Too dense next to the thin Latin; flatter stroke contrast (U+3161 vs U+3163 ≈ 0.83) |
| **Maru Buri Regular** | Best balance; more stroke contrast (≈ 0.74) |
| Maru Buri Light | Latin dominates; Hangul looks weak |
| Maru Buri ExtraLight | Far too light |

Chosen by stroke-contrast measurement plus visual judgement. To retry RIDIBatang, point `[hangul.files]` at it and set `embolden` for Bold.
