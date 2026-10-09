#!/usr/bin/env python3
"""Build a font package.

  python scripts/build.py jeongdok                 # all targets
  python scripts/build.py jeongdok --only ttf,web  # selected targets
  python scripts/build.py --list

Targets: kind=graft: ttf, kf, cpfont, web   |   kind=nerd-patch: nerd, web
Output:  packages/<pkg>/dist/eink/{ttf,kf,cpfont}  packages/<pkg>/dist/web/static
"""
import argparse
import os
import sys
import tomllib
from pathlib import Path

# reproducible output: fontTools honours SOURCE_DATE_EPOCH for head.modified
os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import nerd  # noqa: E402
from lib.targets import TARGETS as GRAFT_TARGETS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    "graft": (["ttf", "kf", "cpfont", "web"], GRAFT_TARGETS),
    "nerd-patch": (["nerd", "web"], {"nerd": nerd.build_nerd, "web": nerd.build_web}),
}


def packages():
    return sorted(p.parent.name for p in (ROOT / "packages").glob("*/font.toml"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package", nargs="?")
    ap.add_argument("--only", help="comma-separated targets")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.package:
        print("\n".join(packages()))
        return
    pkg = ROOT / "packages" / a.package
    cfg = tomllib.loads((pkg / "font.toml").read_text())
    order, targets = KINDS[cfg.get("kind", "graft")]
    want = a.only.split(",") if a.only else cfg.get("targets", order)
    for t in order:
        if t in want:
            print(f"[{a.package}] {t}")
            targets[t](pkg, cfg)


if __name__ == "__main__":
    main()
