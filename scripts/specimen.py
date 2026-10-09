#!/usr/bin/env python3
"""Render docs/specimen/index.html to docs/specimen/typography-specimen.pdf with headless Chromium.

  uv run scripts/specimen.py [--browser chromium]

Needs: a Chromium/Chrome binary, network access for the IBM Plex Sans KR stylesheet (Google Fonts),
and built web fonts (dist/web) of jeongdok, jeongdok-display and d2koding.
"""
import argparse
import functools
import http.server
import json
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render_template():
    """docs/specimen/index.template.html + copy.ko.json -> index.html. Copy values are trusted HTML."""
    doc = ROOT / "docs" / "specimen"
    tpl = (doc / "index.template.html").read_text(encoding="utf-8")
    copy = json.loads((doc / "copy.ko.json").read_text(encoding="utf-8"))
    used = set(re.findall(r"\{\{(\w+)\}\}", tpl))
    if used != set(copy):
        sys.exit(f"template/copy mismatch: missing {sorted(used - set(copy))}, unused {sorted(set(copy) - used)}")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: copy[m.group(1)], tpl)
    (doc / "index.html").write_text(out, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser")
    a = ap.parse_args()
    exe = a.browser or next((b for b in ("chromium", "google-chrome-stable", "google-chrome", "chrome") if shutil.which(b)), None)
    if not exe:
        sys.exit("no Chromium/Chrome found; pass --browser")
    for pkg in ("jeongdok", "jeongdok-display", "d2koding"):
        if not (ROOT / "packages" / pkg / "dist" / "web" / "static").exists():
            sys.exit(f"run scripts/build.py {pkg} first")
    render_template()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *args, **kw: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    out = ROOT / "docs" / "specimen" / "typography-specimen.pdf"
    url = f"http://127.0.0.1:{srv.server_port}/docs/specimen/index.html"
    cmd = [exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
           f"--print-to-pdf={out}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    srv.shutdown()
    if not out.exists():
        sys.exit(r.stderr[-1500:])
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
