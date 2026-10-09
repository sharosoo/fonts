"""Graft Hangul glyphs from one OFL font onto a Latin TrueType font."""
from __future__ import annotations

import pathops
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram

LICENSE_TEXT = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"


def set_names(font: TTFont, *, family: str, ps: str, style: str, version: str, copyright: str, url: str) -> None:
    name = font["name"]
    style = "Bold Italic" if style == "BoldItalic" else style
    sty = style.replace(" ", "")
    ids = {0: copyright, 1: family, 2: style, 3: f"{ps}-{sty}:Version {version}",
           4: f"{family} {style}", 5: f"Version {version}", 6: f"{ps}-{sty}",
           13: LICENSE_TEXT, 14: LICENSE_URL, 16: family, 17: style, 18: f"{family} {style}"}
    if url:
        ids[11] = url
    name.names = [r for r in name.names if r.nameID not in ids and r.nameID not in (7, 25)]
    for nid, text in ids.items():
        name.setName(text, nid, 3, 1, 0x409)
        name.setName(text, nid, 1, 0, 0)
    try:
        font["head"].fontRevision = float(".".join(version.split(".")[:2]))
    except ValueError:
        pass


def graft(latin_path, hangul_path, out_path, *, scale, dy, track, embolden, ranges, names, style=None):
    lat = TTFont(latin_path)
    han = TTFont(hangul_path)
    upm = lat["head"].unitsPerEm
    hupm = han["head"].unitsPerEm
    is_cff = "CFF " in han
    hcmap = han.getBestCmap()
    lcmap = lat.getBestCmap()
    hgs = han.getGlyphSet()
    hhmtx = han["hmtx"]

    cps = [cp for lo, hi in ranges for cp in range(lo, hi + 1) if cp in hcmap and cp not in lcmap]
    s = upm / hupm * scale
    glyf = lat["glyf"]
    order = lat.getGlyphOrder()[:]
    hmtx = lat["hmtx"]
    added = []
    for cp in cps:
        src = hcmap[cp]
        adv_src = hhmtx[src][0]
        adv = round(adv_src * upm / hupm * track)
        xshift = (adv - adv_src * s) / 2
        tt = TTGlyphPen(None)
        if embolden > 0:
            p = pathops.Path()
            hgs[src].draw(p.getPen(glyphSet=hgs))
            st = pathops.Path(p)
            st.stroke(2 * embolden * hupm, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
            st.convertConicsToQuads()
            u = pathops.op(p, st, pathops.PathOp.UNION, fix_winding=True, keep_starting_points=False)
            u.convertConicsToQuads()
            q = Cu2QuPen(tt, max_err=1.0, reverse_direction=False)
            u.draw(TransformPen(q, (s, 0, 0, s, xshift, dy * upm)))
        else:
            q = Cu2QuPen(tt, max_err=1.0, reverse_direction=is_cff) if is_cff else tt
            hgs[src].draw(TransformPen(q, (s, 0, 0, s, xshift, dy * upm)))
        g = tt.glyph()
        gname = f"uni{cp:04X}"
        if gname in glyf.glyphs:
            continue
        glyf.glyphs[gname] = g
        order.append(gname)
        g.recalcBounds(glyf)
        hmtx.metrics[gname] = (adv, g.xMin if g.numberOfContours else 0)
        added.append((cp, gname))

    lat.setGlyphOrder(order)
    glyf.glyphOrder = order
    for t in lat["cmap"].tables:
        if t.format == 4 and t.platformID in (0, 3):
            for cp, gname in added:
                if cp <= 0xFFFF:
                    t.cmap[cp] = gname

    # no TrueType bytecode: KF builds strip it, and grafted glyphs carry none
    for tag in ("fpgm", "prep", "cvt "):
        if tag in lat:
            del lat[tag]
    for gname in order:
        p = ttProgram.Program()
        p.fromBytecode(b"")
        glyf.glyphs[gname].program = p
    mp = lat["maxp"]
    mp.maxFunctionDefs = mp.maxInstructionDefs = mp.maxStorage = 0
    mp.maxStackElements = mp.maxTwilightPoints = mp.maxSizeOfInstructions = 0

    os2 = lat["OS/2"]
    os2.ulUnicodeRange1 |= 1 << 28
    os2.ulUnicodeRange2 |= (1 << (56 - 32)) | (1 << (52 - 32)) | (1 << (48 - 32))
    os2.ulCodePageRange1 |= 1 << 19

    for tag in ("STAT", "fvar", "avar", "gvar", "HVAR", "MVAR", "VVAR"):
        if tag in lat:
            del lat[tag]
    style = style or lat["name"].getDebugName(2) or "Regular"
    set_names(lat, style=style, **names)
    # style flags must follow the requested style, not the donor file (variable instances keep "Regular")
    bold, ital = "Bold" in style, "Italic" in style
    os2.fsSelection = (os2.fsSelection & ~0x61) | (1 if ital else 0) | (0x20 if bold else 0) | (0x40 if not (bold or ital) else 0)
    lat["head"].macStyle = (1 if bold else 0) | (2 if ital else 0)
    os2.usWeightClass = 700 if bold else 400
    lat.save(out_path)
    return len(added)
