"""Build targets: ttf (graft), kf (Kobo), cpfont (CrossPoint), web (woff2 + css)."""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

from .graft import graft

ROOT = Path(__file__).resolve().parents[2]
STYLE_CSS = {"Regular": (400, "normal"), "Italic": (400, "italic"), "Bold": (700, "normal"), "BoldItalic": (700, "italic")}


# ---------------------------------------------------------------- ttf
def _graft_job(a):
    return graft(**a)


def _instance_latin(pkg: Path, cfg: dict, style: str, tmp: Path) -> str:
    """Static Latin master for `style`: either a static file pattern or an instance of a variable font."""
    lat = cfg["latin"]
    if "variable" not in lat:
        return str(pkg / lat["pattern"].format(style=style))
    from fontTools.ttLib.removeOverlaps import removeOverlaps
    from fontTools.varLib import instancer
    src = pkg / lat["variable"]["italic" if "Italic" in style else "roman"]
    f = instancer.instantiateVariableFont(TTFont(src), lat["axes"][style])
    removeOverlaps(f)   # variable masters keep overlapping contours; Kobo/older rasterizers dislike them
    out = tmp / f"latin-{style}.ttf"
    f.save(out)
    return str(out)


def build_ttf(pkg: Path, cfg: dict) -> None:
    from .fetch import ensure_fetch
    ensure_fetch(pkg, cfg)
    fam, hg = cfg["family"], cfg["hangul"]
    out = pkg / "dist" / "eink" / "ttf"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pkg / "dist" / "_tmp_latin"
    tmp.mkdir(parents=True, exist_ok=True)
    jobs = []
    for style in fam["styles"]:
        hfile = hg["files"][style] if "files" in hg else hg["file"]
        jobs.append(dict(
            style=style,
            latin_path=_instance_latin(pkg, cfg, style, tmp),
            hangul_path=str(pkg / hfile),
            out_path=str(out / f"{fam['ps_name']}-{style}.ttf"),
            scale=hg["scale"], dy=hg["dy"], track=hg["track"],
            embolden=hg["embolden"][style], ranges=hg["ranges"],
            names=dict(family=fam["name"], ps=fam["ps_name"], version=fam["version"],
                       copyright=fam["copyright"], url=fam.get("url", "")),
        ))
    with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
        for style, n in zip(fam["styles"], ex.map(_graft_job, jobs)):
            print(f"  ttf {style}: grafted {n} glyphs")
    shutil.rmtree(tmp)


# ---------------------------------------------------------------- tools
def _tools_dir() -> Path:
    d = ROOT / "tools" / "vendor"
    if not (d / "kobofix.py").exists() or not (d / "fontconvert_sdcard.py").exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "fetch_tools.py")], check=True)
    return d


def _ots_path() -> str:
    import ots
    d = Path(ots.__file__).parent
    if not (d / "ots-sanitize").exists():
        raise RuntimeError("ots-sanitize binary not found in opentype-sanitizer package")
    tmp = Path(tempfile.mkdtemp(prefix="ots-bin-"))
    (tmp / "ots-sanitize").symlink_to(d / "ots-sanitize")
    return str(tmp) + os.pathsep + os.environ["PATH"]


# ---------------------------------------------------------------- kf
def build_kf(pkg: Path, cfg: dict) -> None:
    fam = cfg["family"]
    src = pkg / "dist" / "eink" / "ttf"
    out = pkg / "dist" / "eink" / "kf"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as td:
        files = []
        for style in fam["styles"]:
            dst = Path(td) / f"{fam['ps_name']}-{style}.ttf"
            shutil.copy2(src / dst.name, dst)
            files.append(str(dst))
        env = dict(os.environ, PATH=_ots_path())
        r = subprocess.run([sys.executable, str(_tools_dir() / "kobofix.py"), "--preset", "kf", *files],
                           env=env, capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
            raise RuntimeError("kobofix failed")
        ok = re.findall(r"ots-sanitize: (\w+)", r.stdout + r.stderr)
        print("  kf: ots-sanitize", ok)
        produced = sorted(Path(td).glob("KF_*.ttf"))
        if len(produced) != len(fam["styles"]):
            raise RuntimeError(f"expected {len(fam['styles'])} KF fonts, got {len(produced)}")
        for p in produced:
            shutil.move(str(p), out / p.name)


# ---------------------------------------------------------------- cpfont
def build_cpfont(pkg: Path, cfg: dict) -> None:
    fam, cp = cfg["family"], cfg["cpfont"]
    src = pkg / "dist" / "eink" / "ttf"
    out = pkg / "dist" / "eink" / "cpfont" / fam["name"]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    flags = {"Regular": "--regular", "Bold": "--bold", "Italic": "--italic", "BoldItalic": "--bolditalic"}
    fl = shutil.which("font-line") or str(Path(sys.executable).parent / "font-line")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cmd = [sys.executable, str(_tools_dir() / "fontconvert_sdcard.py"), "--intervals", cp["intervals"],
               "--sizes", ",".join(map(str, cp["sizes"])), "--name", fam["name"], "--output-dir", str(td / "o")]
        for style, flag in flags.items():
            dst = td / f"{fam['ps_name']}-{style}.ttf"
            shutil.copy2(src / dst.name, dst)
            subprocess.run([fl, "percent", str(cp["line_percent"]), str(dst)], check=True, capture_output=True)
            relaxed = dst.with_name(f"{dst.stem}-linegap{cp['line_percent']}.ttf")
            with TTFont(relaxed) as f:
                f["OS/2"].sTypoAscender = f["hhea"].ascent
                f["OS/2"].sTypoDescender = f["hhea"].descent
                f["OS/2"].sTypoLineGap = f["hhea"].lineGap
                f.save(relaxed)
            cmd += [flag, str(relaxed)]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(_tools_dir()))
        if r.returncode:
            sys.stderr.write(r.stderr[-3000:])
            raise RuntimeError("cpfont converter failed")
        for p in sorted((td / "o").glob("*.cpfont")):
            shutil.copy2(p, out / p.name)
            print(f"  cpfont {p.name}: {p.stat().st_size / 1048576:.1f} MB")


# ---------------------------------------------------------------- web
def _parse_slices(css_path: Path):
    css = css_path.read_text()
    out = []
    for blk in re.findall(r"@font-face\s*{[^}]*}", css):
        m = re.search(r"unicode-range:\s*([^;]+);", blk)
        cps = set()
        for part in m.group(1).split(","):
            part = part.strip()[2:]
            if "-" in part:
                a, b = part.split("-")
                cps.update(range(int(a, 16), int(b, 16) + 1))
            else:
                cps.add(int(part, 16))
        out.append(cps)
    return out


def _ranges_css(cps):
    cps = sorted(cps)
    parts, s, p = [], cps[0], cps[0]
    for c in cps[1:]:
        if c == p + 1:
            p = c
            continue
        parts.append((s, p))
        s = p = c
    parts.append((s, p))
    return ", ".join(f"U+{a:X}" if a == b else f"U+{a:X}-{b:X}" for a, b in parts)


def _ks_hangul():
    ks = set()
    for hi in range(0xB0, 0xC9):
        for lo in range(0xA1, 0xFF):
            try:
                ch = bytes([hi, lo]).decode("euc-kr")
            except Exception:
                continue
            if 0xAC00 <= ord(ch) <= 0xD7A3:
                ks.add(ord(ch))
    return ks


_cache: dict = {}


def _subset_job(a):
    path, unicodes, out_path = a
    if path not in _cache:
        _cache[path] = Path(path).read_bytes()
    f = TTFont(io.BytesIO(_cache[path]))
    o = subset.Options()
    o.layout_features = ["*"]
    o.notdef_outline = True
    o.hinting = False
    o.name_IDs = ["*"]
    o.name_languages = ["*"]
    o.glyph_names = False
    o.flavor = "woff2"
    s = subset.Subsetter(o)
    s.populate(unicodes=unicodes)
    s.subset(f)
    f.flavor = "woff2"
    f.save(out_path)


def _face(family, style, url, rng=None):
    w, st = STYLE_CSS[style]
    r = f"\n  unicode-range: {rng};" if rng else ""
    return (f"@font-face {{\n  font-family: '{family}';\n  font-style: {st};\n  font-weight: {w};\n  font-display: swap;\n"
            f"  src: url('{url}') format('woff2');{r}\n}}\n")


def build_web(pkg: Path, cfg: dict) -> None:
    fam = cfg["family"]
    ps, name = fam["ps_name"], fam["name"]
    lower = fam.get("slug", name.lower())
    src = pkg / "dist" / "eink" / "ttf"
    out = pkg / "dist" / "web" / "static"
    if out.exists():
        shutil.rmtree(out)
    for d in ("woff2", "woff2-subset", "woff2-dynamic-subset"):
        (out / d).mkdir(parents=True)
    allcps = set(TTFont(src / f"{ps}-Regular.ttf").getBestCmap())
    hangul = {c for c in allcps if 0xAC00 <= c <= 0xD7A3}
    sub_cps = (allcps - hangul) | (hangul & _ks_hangul())
    slices = _parse_slices(ROOT / cfg["web"]["slices"])
    covered = set().union(*slices)
    dyn = [sl & allcps for sl in slices if sl & allcps]
    left = allcps - covered
    if left:
        dyn.append(left)
    print(f"  web: {len(dyn)} dynamic slices (leftover {len(left)} chars), KS X 1001 subset {len(sub_cps)} chars")
    jobs = []
    for st in fam["styles"]:
        p = str(src / f"{ps}-{st}.ttf")
        jobs.append((p, allcps, str(out / "woff2" / f"{ps}-{st}.woff2")))
        jobs.append((p, sub_cps, str(out / "woff2-subset" / f"{ps}-{st}.subset.woff2")))
        for i, cps in enumerate(dyn):
            jobs.append((p, cps, str(out / "woff2-dynamic-subset" / f"{ps}-{st}.subset.{i}.woff2")))
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        list(ex.map(_subset_job, jobs, chunksize=4))
    full = "".join(_face(name, st, f"./woff2/{ps}-{st}.woff2") for st in fam["styles"])
    sub = "".join(_face(name, st, f"./woff2-subset/{ps}-{st}.subset.woff2") for st in fam["styles"])
    dcss = "".join(_face(name, st, f"./woff2-dynamic-subset/{ps}-{st}.subset.{i}.woff2", _ranges_css(c))
                   for st in fam["styles"] for i, c in enumerate(dyn))
    (out / f"{lower}.css").write_text(full)
    (out / f"{lower}-subset.css").write_text(sub)
    (out / f"{lower}-dynamic-subset.css").write_text(dcss)
    print(f"  web: {len(jobs)} woff2 files, 3 css")


TARGETS = {"ttf": build_ttf, "kf": build_kf, "cpfont": build_cpfont, "web": build_web}
