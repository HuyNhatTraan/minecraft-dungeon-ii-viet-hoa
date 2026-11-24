# -*- coding: utf-8 -*-
"""Build MCD2_VH_Launcher.exe as a single file.

Downloads the official WebView2 Runtime standalone installer (x64) into
assets/ first so the resulting exe works on machines without WebView2.
"""
import hashlib
import subprocess
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
INSTALLER = ASSETS / "WebView2RuntimeInstallerX64.exe"

WEBVIEW2_URL = (
    "https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/"
    "22ced09c-d6bd-4427-a658-f1dc48f3a440/MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
)
WEBVIEW2_SHA256 = "82B2D8A7013E0C0EA15D48FF4742EE3778BA16BD8B7B4A47876645B3E48D4016"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_webview2_installer():
    if INSTALLER.exists() and sha256(INSTALLER).upper() == WEBVIEW2_SHA256:
        print("[ok] WebView2 installer already present")
        return
    print("[..] downloading WebView2 Runtime standalone (x64), ~200 MB")
    req = urllib.request.Request(WEBVIEW2_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=600) as r, INSTALLER.open("wb") as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    actual = sha256(INSTALLER).upper()
    if actual != WEBVIEW2_SHA256:
        INSTALLER.unlink(missing_ok=True)
        raise SystemExit(f"[error] WebView2 hash mismatch: {actual}")
    print("[ok] WebView2 installer verified")


def main():
    ensure_webview2_installer()
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--windowed",
        "--name", "MCD2_VH_Launcher",
        "--icon", "assets/logo.ico",
        "--add-data", "ui.html;.",
        "--add-data", "assets;assets",
        "--clean", "--noconfirm",
        "launcher.py",
    ]
    print("[..]", " ".join(cmd))
    subprocess.run(cmd, cwd=str(BASE), check=True)
    exe = BASE / "dist" / "MCD2_VH_Launcher.exe"
    print(f"[done] {exe} ({exe.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
