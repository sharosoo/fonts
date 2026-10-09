#!/usr/bin/env python3
"""Package a built font for release.

  python scripts/release.py jeongdok            # zip assets + SHA256SUMS into packages/jeongdok/dist/release
  python scripts/release.py jeongdok --publish  # also: commit, tag, push, `gh release create`

Release model (same idea as naver/nanumfont-style GitHub releases):
  * e-reader / desktop fonts are downloaded from GitHub Release assets (never committed)
  * web fonts are not committed; CI uploads dist/web/static to
    https://cdn.sharosoo.com/fonts/<package>/v<version>/ when the tag is pushed
Tag format: <package>-v<version>   e.g. jeongdok-v0.1.0
"""
import argparse
import hashlib
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    pkg = ROOT / "packages" / a.package
    cfg = tomllib.loads((pkg / "font.toml").read_text())
    fam = cfg["family"]
    ver = fam["version"]
    if (pkg / "VERSION").read_text().strip() != ver:
        sys.exit(f"VERSION file != font.toml version ({ver})")
    name = fam["name"]
    d = pkg / "dist"
    out = d / "release"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*"):
        old.unlink()
    extras = [pkg / "OFL.txt", pkg / "CREDITS.md"]

    def bundle(zname, files):
        with zipfile.ZipFile(out / zname, "w", zipfile.ZIP_DEFLATED) as z:
            for f, arc in files:
                z.write(f, arc)

    web_root = d / "web" / "static"
    web = sorted(p for p in web_root.rglob("*") if p.is_file())
    ex = [(p, p.name) for p in extras]
    if cfg.get("kind", "graft") == "nerd-patch":
        nerd = sorted((d / "eink" / "nerd").rglob("*.ttf"))
        if not (nerd and web):
            sys.exit("missing build output; run scripts/build.py first")
        bundle(f"{fam['ps_name']}-{ver}-nerd.zip", [(p, f"{p.parent.name}/{p.name}") for p in nerd] + ex)
    else:
        ttf = sorted((d / "eink" / "ttf").glob("*.ttf"))
        kf = sorted((d / "eink" / "kf").glob("*.ttf"))
        cp = sorted((d / "eink" / "cpfont" / name).glob("*.cpfont"))
        wants = cfg.get("targets", ["ttf", "kf", "cpfont", "web"])
        if not (ttf and web) or ("kf" in wants and not kf) or ("cpfont" in wants and not cp):
            sys.exit("missing build output; run scripts/build.py first")
        bundle(f"{fam['ps_name']}-{ver}-desktop.zip", [(p, p.name) for p in ttf] + ex)
        if "kf" in wants:
            bundle(f"{fam['ps_name']}-{ver}-kobo.zip", [(p, p.name) for p in kf] + ex)
        if "cpfont" in wants:
            bundle(f"{fam['ps_name']}-{ver}-crosspoint.zip", [(p, f"{name}/{p.name}") for p in cp] + ex)
    bundle(f"{fam['ps_name']}-{ver}-web.zip", [(p, str(p.relative_to(web_root))) for p in web] + ex)
    sums = []
    for z in sorted(out.glob("*.zip")):
        sums.append(f"{hashlib.sha256(z.read_bytes()).hexdigest()}  {z.name}")
        print(f"  {z.name}  {z.stat().st_size / 1048576:.1f} MB")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")

    tag = f"{a.package}-v{ver}"
    notes = f"## {name} {ver}\n\nSee packages/{a.package}/CHANGELOG.md. Web fonts: https://cdn.sharosoo.com/fonts/{a.package}/v{ver}/{a.package}-dynamic-subset.css\n"
    (out / "NOTES.md").write_text(notes)
    cmds = [
        ["git", "add", f"packages/{a.package}", "scripts", "README.md"],
        ["git", "commit", "-m", f"release({a.package}): v{ver}"],
        ["git", "tag", "-a", tag, "-m", f"{name} {ver}"],
        ["git", "push", "origin", "HEAD", tag],
        ["gh", "release", "create", tag, *map(str, sorted(out.glob("*.zip"))), str(out / "SHA256SUMS"),
         "--title", f"{name} {ver}", "--notes-file", str(out / "NOTES.md")],
    ]
    if not a.publish:
        print("\nDry run. To publish:")
        for c in cmds:
            print("  " + " ".join(c))
        return
    for c in cmds:
        subprocess.run(c, check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
