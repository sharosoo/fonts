"""Pinned downloads (sha256-verified)."""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}


def download(url: str, dest: Path, sha256: str | None) -> Path:
    if dest.exists() and (not sha256 or hashlib.sha256(dest.read_bytes()).hexdigest() == sha256):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  download {url}")
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    got = hashlib.sha256(data).hexdigest()
    if sha256 and got != sha256:
        raise RuntimeError(f"sha256 mismatch for {url}: {got}")
    dest.write_bytes(data)
    return dest


def ensure_fetch(pkg: Path, cfg: dict) -> None:
    """[[fetch]] entries in font.toml (dest is relative to the package).

    plain file:   {url, sha256, dest}
    zip member:   {url, sha256 (of the zip), member, dest, member_sha256 (optional)}
    """
    import zipfile
    for item in cfg.get("fetch", []):
        dest = pkg / item["dest"]
        if "member" not in item:
            download(item["url"], dest, item.get("sha256"))
            continue
        want = item.get("member_sha256")
        if dest.exists() and (not want or hashlib.sha256(dest.read_bytes()).hexdigest() == want):
            continue
        z = download(item["url"], pkg / "upstream" / "cache" / Path(item["url"]).name, item.get("sha256"))
        with zipfile.ZipFile(z) as zf:
            data = zf.read(item["member"])
        if want and hashlib.sha256(data).hexdigest() != want:
            raise RuntimeError(f"sha256 mismatch for {item['member']}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
