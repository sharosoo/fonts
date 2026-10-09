"""Nerd Font patch + web build for packages with kind = "nerd-patch" (e.g. d2koding).

nerd : fetch pinned upstream fonts, run Nerd Fonts font-patcher (FontForge) inside a container
web  : woff2 sets from the *unpatched* upstream (renamed), plus a PUA-only symbol font taken from the
       patched Mono build, joined by unicode-range so code blocks can use Nerd icons on demand.
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

from .fetch import UA, download as _download  # noqa: F401
from .graft import set_names
from .targets import ROOT, _face, _parse_slices, _ranges_css, _subset_job, STYLE_CSS

UA = {"User-Agent": "Mozilla/5.0"}


def fetch_upstream(pkg: Path, cfg: dict) -> dict[str, Path]:
    """Return {key: path} of the upstream TTFs, downloading the pinned release zip when needed."""
    up = cfg["upstream"]
    cache = pkg / "upstream" / "cache"
    zpath = cache / "release.zip"
    _download(up["zip_url"], zpath, up["zip_sha256"])
    out = {}
    with zipfile.ZipFile(zpath) as z:
        for key, member in up["files"].items():
            dst = cache / Path(member).name
            if not dst.exists():
                dst.write_bytes(z.read(member))
            out[key] = dst
        lic = cache / "OFL.txt"
        if not lic.exists() and "OFL.txt" in z.namelist():
            lic.write_bytes(z.read("OFL.txt"))
    return out


def fetch_patcher(cfg: dict) -> Path:
    n = cfg["nerd"]
    root = ROOT / "tools" / "vendor" / f"nerd-fonts-{n['version']}"
    if not (root / "font-patcher").exists():
        z = ROOT / "tools" / "vendor" / f"FontPatcher-{n['version']}.zip"
        _download(n["patcher_url"], z, n["patcher_sha256"])
        root.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(z).extractall(root)
    return root


def _patch_job(a):
    image, patcher, src, outdir, flags = a
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = ["podman", "run", "--rm", "-v", f"{patcher}:/patcher:ro", "-v", f"{src.parent}:/in:ro", "-v", f"{outdir}:/out",
           image, "python3", "/patcher/font-patcher", "--complete", "--quiet", "--no-progressbars", *flags, "-out", "/out", f"/in/{src.name}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return src.name, flags


def build_nerd(pkg: Path, cfg: dict) -> None:
    fonts = fetch_upstream(pkg, cfg)
    patcher = fetch_patcher(cfg)
    image = cfg["nerd"]["image"]
    out = pkg / "dist" / "eink" / "nerd"
    if out.exists():
        shutil.rmtree(out)
    jobs = []
    for vname, flags in cfg["nerd"]["variants"].items():
        for key, path in fonts.items():
            jobs.append((image, patcher, path, out / vname, flags))
    with ThreadPoolExecutor(max_workers=min(8, len(jobs))) as ex:
        for name, flags in ex.map(_patch_job, jobs):
            print(f"  patched {name} {' '.join(flags)}")
    # The patcher marks non-"--mono" output as proportional; upstream D2Coding is flagged fixed-pitch
    # (Latin 1 cell, Hangul 2 cells), so restore that on the single-width-icon variants.
    for p in sorted((out / "mono").glob("*.ttf")):
        f = TTFont(p)
        f["post"].isFixedPitch = 1
        f["OS/2"].panose.bProportion = 9
        f.save(p)
    for p in sorted(out.rglob("*.ttf")):
        f = TTFont(p)
        print(f"  {p.relative_to(out)}  family={f['name'].getDebugName(1)!r} full={f['name'].getDebugName(4)!r} {p.stat().st_size / 1048576:.1f} MB")


def _symbols_font(patched: Path, out: Path, ps_family: str, version: str, copyright: str, lo: int, hi: int) -> list[int]:
    f = TTFont(patched)
    cm = f.getBestCmap()
    pua = {c for c in cm if lo <= c <= hi}
    o = subset.Options()
    o.layout_features = []
    o.notdef_outline = True
    o.hinting = False
    o.name_IDs = ["*"]
    o.flavor = "woff2"
    s = subset.Subsetter(o)
    s.populate(unicodes=pua)
    s.subset(f)
    set_names(f, family=ps_family, ps=ps_family.replace(" ", ""), style="Regular", version=version, copyright=copyright, url="")
    f.flavor = "woff2"
    f.save(out)
    return sorted(pua)


def build_web(pkg: Path, cfg: dict) -> None:
    fam = cfg["family"]
    name = fam["name"]
    lower = fam.get("slug", name.lower())
    fonts = fetch_upstream(pkg, cfg)
    web = cfg["web"]
    out = pkg / "dist" / "web" / "static"
    if out.exists():
        shutil.rmtree(out)
    for d in ("woff2", "woff2-dynamic-subset"):
        (out / d).mkdir(parents=True)
    tmp = pkg / "dist" / "_tmp_renamed"
    tmp.mkdir(parents=True, exist_ok=True)
    # web uses the ligature build only; plain text = `font-variant-ligatures: none`
    renamed = {}
    for style, key in (("Regular", web["regular"]), ("Bold", web["bold"])):
        f = TTFont(fonts[key])
        set_names(f, family=name, ps=fam["ps_name"], style=style, version=fam["version"],
                  copyright=fam["copyright"], url=fam.get("url", ""))
        p = tmp / f"{fam['ps_name']}-{style}.ttf"
        f.save(p)
        renamed[style] = p
    allcps = set(TTFont(renamed["Regular"]).getBestCmap()) - {c for c in range(0xE000, 0xF900)}
    slices = _parse_slices(ROOT / web["slices"])
    covered = set().union(*slices)
    dyn = [sl & allcps for sl in slices if sl & allcps]
    left = allcps - covered
    if left:
        dyn.append(left)
    jobs = []
    for st, p in renamed.items():
        jobs.append((str(p), allcps, str(out / "woff2" / f"{fam['ps_name']}-{st}.woff2")))
        for i, cps in enumerate(dyn):
            jobs.append((str(p), cps, str(out / "woff2-dynamic-subset" / f"{fam['ps_name']}-{st}.subset.{i}.woff2")))
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        list(ex.map(_subset_job, jobs, chunksize=4))
    # nerd symbols (PUA only) from the patched Mono Regular
    mono = sorted((pkg / "dist" / "eink" / "nerd" / "mono").glob(web["symbols_from"]))
    if not mono:
        raise RuntimeError("run the nerd target first (symbols are taken from the patched Mono font)")
    parts = [("NerdSymbols", 0xE000, 0xF8FF, "U+E000-F8FF"),            # BMP private use: Powerline, Seti, Devicons, Codicons, FA, Octicons ...
             ("NerdSymbolsMaterial", 0xF0000, 0xFFFFD, "U+F0000-FFFFD")]  # Material Design Icons (large)
    sym_info = []
    for suffix, lo, hi, rng in parts:
        sp = out / "woff2" / f"{fam['ps_name']}-{suffix}.woff2"
        pua = _symbols_font(mono[0], sp, f"{name} {suffix}", fam["version"], fam["copyright"], lo, hi)
        sym_info.append((sp.name, rng, len(pua), sp.stat().st_size // 1024))
    shutil.rmtree(tmp)

    def sym_faces(prefix):
        return "".join(
            f"@font-face {{\n  font-family: '{name}';\n  font-style: normal;\n  font-weight: {w};\n  font-display: swap;\n"
            f"  src: url('{prefix}/{fn}') format('woff2');\n  unicode-range: {rng};\n}}\n"
            for fn, rng, _, _ in sym_info for w in (400, 700))

    full = "".join(_face(name, st, f"./woff2/{fam['ps_name']}-{st}.woff2") for st in ("Regular", "Bold"))
    dcss = "".join(_face(name, st, f"./woff2-dynamic-subset/{fam['ps_name']}-{st}.subset.{i}.woff2", _ranges_css(c))
                   for st in ("Regular", "Bold") for i, c in enumerate(dyn))
    (out / f"{lower}.css").write_text(full + sym_faces("./woff2"))
    (out / f"{lower}-dynamic-subset.css").write_text(dcss + sym_faces("./woff2"))
    print(f"  web: {len(dyn)} slices, {len(jobs)} woff2; nerd symbols: " + ", ".join(f"{n} {g} glyphs {k} KB" for n, _, g, k in sym_info))
