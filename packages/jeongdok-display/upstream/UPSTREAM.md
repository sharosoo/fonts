# Upstream sources

## Newsreader (Latin), committed

`upstream/newsreader/`: unmodified copy of google/fonts `ofl/newsreader` (variable; axes `opsz` 6–72, `wght`).

| File | SHA-256 |
|---|---|
| Newsreader[opsz,wght].ttf | 8a08d13f8a6c0d51be379a60af84f945f65369a67e509ee3c3bdcc421254d7c1 |
| Newsreader-Italic[opsz,wght].ttf | 796668611f80b64d5adf182fde3b6f29ed83b4e7cbec7b96937e84ac01364792 |

The build instantiates `opsz` 72 at `wght` 400 and 700 and removes overlaps.

## Maru Buri (Hangul), downloaded at build time

Fetched by `[[fetch]]` in `font.toml` and hash-checked.

- Source: NAVER's official release, https://hangeul.naver.com/font/maru (`hangeul.pstatic.net/0/hangeul/2022/zip_v2/maruburi.zip`), Version 2.000.
- The zip is cached in `upstream/cache/` (gitignored, 45 MB); only the two TTFs below are used.

| Item | SHA-256 |
|---|---|
| maruburi.zip | 39e3bb6a00b4543563a745195a6a89282c5a1f0f8b71923ff15c1bc7c135fa0c |
| TTF/MaruBuri-Regular.ttf | 254abb4c131316e10a55e04495211f1df8cf68c9f58929375311a41af77c4b9b |
| TTF/MaruBuri-Bold.ttf | 092cb186de18d49adb55721257a63b33f0c9eebb3c7d495336082c3f1e7bdc0d |
