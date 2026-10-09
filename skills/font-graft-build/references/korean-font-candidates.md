# Korean font candidates (donors and sans metrics)

Metric method: PIL render, anchor `ls` on a tall canvas, em units. V = vertical stem of `ㅣ`, H = horizontal stroke of `ㅡ`, ink = ink area / em² averaged over ~30 common syllables. The values below are not reproducible from files in this repository (the comparison fonts are not pinned here); treat them as recorded measurements.

## Type system
Roles: UI sans, long-form serif, code mono (Hangul at 2 cells), display/brand. Numerals: sans `tnum`, not a separate font. Chosen set (`docs/TYPOGRAPHY_SETUP.md`):

| Role | Font |
|---|---|
| Body serif | Jeongdok (Libron + RIDIBatang) |
| Headings / brand | Jeongdok Display (Newsreader opsz 72 + Maru Buri) |
| UI sans | IBM Plex Sans KR, unmodified from Google Fonts |
| Code | D2Koding (D2Coding + Nerd Fonts, ligature) |

## Sans measured against Jeongdok
Reference (Jeongdok): Latin x-height 0.532, Hangul face 0.866, V 0.075, H/V 0.83, ink 0.186.

| Sans | x-height | face | V | H/V | ink | Note |
|---|---|---|---|---|---|---|
| Pretendard | 0.530 | 0.845 | 0.077 | 0.87 | 0.192 | closest |
| IBM Plex Sans KR | 0.515 | 0.868 | 0.077 | – | 0.192 | chosen; more technical |
| Wanted Sans | 0.505 | 0.843 | 0.075 | 0.83 | 0.192 | geometric, humanist touches |
| Noto Sans KR w400 | – | – | – | – | 0.214 | heavy |
| Gowun Dodum | – | – | 0.062 | – | 0.155 | light; headings, not body |
| Nanum Gothic | – | 0.902 | – | – | 0.190 | |

Not measured: SUIT, Spoqa Han Sans Neo, NanumSquare Neo.

## Hangul donors
| Donor | Source | Metrics and notes |
|---|---|---|
| Maru Buri | NAVER, https://hangeul.naver.com/font/maru (pinned in `packages/jeongdok-display/font.toml`) | V 0.069, H/V 0.72 (Regular); Latin x-height only 0.468 |
| RIDIBatang | RIDI/Sandoll, https://ridicorp.com/ridibatang/; the name is a trademark | V 0.081, H 0.067, H/V 0.83. Community `ridibatang-9` ships -5/-7/-9 % tracking builds without a LICENSE |

Other donors (Noto Serif KR, Hahmlet, Gowun Batang, Nanum Myeongjo) have not been vetted here; read the upstream license before use.

## Pairing rule
- The Hangul donor's stroke contrast should echo the Latin's. Newsreader opsz 72 has hairline/stem ~0.22: RIDIBatang (H/V 0.83) is too dense, Maru Buri Regular (H/V ~0.72) balances best; Light/ExtraLight are too weak. Body-size Latin (flatter contrast) pairs with RIDIBatang.
- Keep the donor selectable per style in `font.toml` (`[hangul.files]`).

## Display / brand alternatives
Hahmlet, Gowun Batang Bold, Gmarket Sans, Paperlogy. Unvetted; check coverage and license at the source first.
