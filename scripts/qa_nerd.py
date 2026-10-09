#!/usr/bin/env python3
"""QA for nerd-patch packages: ligatures kept, icons present, widths, names."""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
pkg = ROOT / "packages" / (sys.argv[1] if len(sys.argv) > 1 else "d2koding")
bad = 0
for p in sorted((pkg / "dist" / "eink" / "nerd").rglob("*.ttf")):
    f = TTFont(p)
    cm = f.getBestCmap()
    h = f["hmtx"]
    feats = sorted({fr.FeatureTag for fr in f["GSUB"].table.FeatureList.FeatureRecord}) if "GSUB" in f else []
    lig = "ligature" in p.name.lower()
    has_lig = "calt" in feats or "liga" in feats
    icons = {"powerline E0B0": 0xE0B0, "seti E5FA": 0xE5FA, "devicons E700": 0xE700, "codicon EA60": 0xEA60,
             "FA F000": 0xF000 + 1, "material F0001": 0xF0001, "octicon F400": 0xF400}
    miss = [k for k, c in icons.items() if c not in cm]
    adv = {k: h[cm[ord(k)]][0] for k in "Ai가"}
    icon_adv = h[cm[0xE700]][0] if 0xE700 in cm else None
    from fontTools.pens.boundsPen import BoundsPen
    gs = f.getGlyphSet(); bp = BoundsPen(gs); gs[cm[0xE700]].draw(bp)
    icon_w = int(bp.bounds[2] - bp.bounds[0])
    is_mono = p.parent.name == "mono"
    ok = (has_lig == lig) and not miss and adv["가"] == 1000 and adv["A"] == 500 and (not is_mono or (f["post"].isFixedPitch and icon_w <= 520))
    bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {p.parent.name}/{p.name:44s} lig={has_lig} fixed={f['post'].isFixedPitch} adv(A,i,가)={adv['A']},{adv['i']},{adv['가']} icon_adv={icon_adv} icon_w={icon_w} missing={miss}")
sys.exit(1 if bad else 0)
