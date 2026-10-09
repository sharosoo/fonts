#!/usr/bin/env python3
"""Sanity checks on a built package: names, coverage, ink balance, leftover upstream names."""
import sys, tomllib
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LAT = "the quick brown fox jumps over a lazy dog reading is slow"
HAN = "다람쥐 헌 쳇바퀴에 타고파 읽는 시간의 고요함 물밥꿈책"


def ink_ratio(path, text, px=100):
    font = ImageFont.truetype(str(path), px)
    d0 = ImageDraw.Draw(Image.new("L", (10, 10)))
    tl = d0.textlength(text, font=font)
    base = int(px * 1.6)
    im = Image.new("L", (int(tl) + 40, px * 3), 255)
    ImageDraw.Draw(im).text((20, base), text, font=font, fill=0, anchor="ls")
    return ((255 - np.array(im).astype(float)) / 255).sum() / (tl * px)


def main():
    pkg = ROOT / "packages" / sys.argv[1]
    cfg = tomllib.loads((pkg / "font.toml").read_text())
    if cfg.get("kind") == "nerd-patch":
        import runpy
        sys.argv = ["qa_nerd.py", sys.argv[1]]
        runpy.run_path(str(Path(__file__).with_name("qa_nerd.py")), run_name="__main__")
        return
    fam = cfg["family"]
    banned = cfg.get("qa", {}).get("banned", ["Libron", "Readerly", "Newsreader", "RIDI", "LibRidi"])
    bad = 0
    for st in fam["styles"]:
        p = pkg / "dist" / "eink" / "ttf" / f"{fam['ps_name']}-{st}.ttf"
        f = TTFont(p)
        cm = f.getBestCmap()
        hangul = sum(1 for c in cm if 0xAC00 <= c <= 0xD7A3)
        # banned strings may appear only in copyright (0) and nothing else
        leaks = [(r.nameID, r.toUnicode()) for r in f["name"].names
                 if r.nameID not in (0,) and any(b.lower() in r.toUnicode().lower() for b in banned)]
        bad += len(leaks)
        l, h = ink_ratio(p, LAT), ink_ratio(p, HAN)
        print(f"{st:11s} family={f['name'].getDebugName(1)!r} full={f['name'].getDebugName(4)!r} ps={f['name'].getDebugName(6)!r} "
              f"hangul={hangul}/11172 glyphs={len(f.getGlyphOrder())} hangul/latin ink={h / l:.2f} name-leaks={leaks}")
    print("OK" if not bad else f"FAIL: {bad} reserved-name leaks")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
