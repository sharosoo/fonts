#!/usr/bin/env python3
"""Download pinned third-party build tools into tools/vendor (gitignored).

- kobofix.py            nicoverbruggen/kobo-font-fix  (Kobo KF fonts)
- fontconvert_sdcard.py crosspoint-reader/crosspoint-reader (.cpfont converter)
Pins match the ones Libron uses, so output stays comparable.
"""
import sys
import urllib.request
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "tools" / "vendor"
KOBOFIX = "https://raw.githubusercontent.com/nicoverbruggen/kobo-font-fix/v0.10/kobofix.py"
CP_COMMIT = "2ceeeccd5ae8f2693eef71388d3f0a4137c1fcc9"
CP_BASE = f"https://raw.githubusercontent.com/crosspoint-reader/crosspoint-reader/{CP_COMMIT}/lib/EpdFont/scripts"
FILES = {
    "kobofix.py": KOBOFIX,
    "fontconvert_sdcard.py": f"{CP_BASE}/fontconvert_sdcard.py",
    "cpfont_version.py": f"{CP_BASE}/cpfont_version.py",
}

VENDOR.mkdir(parents=True, exist_ok=True)
for name, url in FILES.items():
    print("fetch", name)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    (VENDOR / name).write_bytes(urllib.request.urlopen(req, timeout=60).read())
print("ok ->", VENDOR)
