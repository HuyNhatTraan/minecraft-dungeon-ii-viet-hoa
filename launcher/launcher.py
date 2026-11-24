# -*- coding: utf-8 -*-
"""MCD2 Vietnamese Launcher - WebView edition (single-file exe)."""
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
import winreg
from pathlib import Path

import webview

if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent

ASSETS = BASE / "assets"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
CONFIG = Path(os.environ.get("LOCALAPPDATA", "")) / "MCD2_VH_Launcher" / "config.json"
CONFIG.parent.mkdir(parents=True, exist_ok=True)

FONT_PATHS_FILE = ASSETS / "font_paths.txt"


def load_font_assets():
    if FONT_PATHS_FILE.exists():
        paths = [p.strip() for p in FONT_PATHS_FILE.read_text(encoding="utf-8").splitlines() if p.strip()]
        if paths:
            return paths
    return [
        "Dungeons/Content/Spicewood/Fonts/Spicewood/Font_Spicewood_Sixteen_Regular.ufont",
        "Dungeons/Content/Spicewood/Fonts/Spicewood/Font_Spicewood_Sixteen_Bold.ufont",
        "Dungeons/Content/Spicewood/Fonts/Spicewood/Font_Spicewood_Sixteen_SemiBold.ufont",
        "Dungeons/Content/Spicewood/Fonts/Spicewood/Font_Spicewood_TenV2_Regular.ufont",
        "Dungeons/Content/Fonts/NotoSans-Regular.ufont",
        "Dungeons/Content/Fonts/NotoSans-Bold.ufont",
    ]


def load_cfg():
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"game_path": "", "font_name": "", "guide_seen": False,
            "volume": 10, "muted": False}


def save_cfg(cfg):
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


CFG = load_cfg()
WINDOW = None


def detect_game():
    guesses = []
    if CFG.get("game_path"):
        guesses.append(Path(CFG["game_path"]))
    guesses.append(Path(sys.executable).resolve().parent)
    guesses.append(Path(r"D:\Games\Minecraft Dungeons II"))
    for g in guesses:
        if (g / "Dungeons.exe").exists():
            return str(g)
    return ""


class Api:
    def _root(self):
        return Path(CFG.get("game_path") or detect_game())

    def _paks(self):
        return self._root() / "Dungeons" / "Content" / "Paks"

    def get_audio(self):
        return {"volume": int(CFG.get("volume", 10)), "muted": bool(CFG.get("muted", False))}

    def set_audio(self, volume, muted):
        CFG["volume"] = max(0, min(100, int(volume)))
        CFG["muted"] = bool(muted)
        save_cfg(CFG)
        return True

    def guide_seen(self):
        return bool(CFG.get("guide_seen", False))

    def set_guide_seen(self):
        CFG["guide_seen"] = True
        save_cfg(CFG)
        return True

    def state(self):
        root = self._root()
        mod_dir = self._paks() / "~mods" / "Dungeons-Vietnamese"
        fresh = load_cfg()  # đọc lại từ đĩa để không bị stale khi đổi font nhiều lần
        CFG.update(fresh)
        return {
            "game_path": str(root),
            "game_found": bool(root and (root / "Dungeons.exe").exists()),
            "mod_installed": bool(mod_dir.exists() and (mod_dir / "Dungeons-Vietnamese_P.pak").exists()),
            "font_name": fresh.get("font_name", ""),
            "version": "1.0.0",
        }

    def set_game_path(self, path):
        p = Path(path)
        if not p.is_dir():
            return {"ok": False, "msg": "Thư mục không tồn tại."}
        CFG["game_path"] = str(p)
        save_cfg(CFG)
        return {"ok": True, "msg": f"Đã chọn: {p}"}

    def pick_game(self):
        if WINDOW is None:
            return None
        result = WINDOW.create_file_dialog(webview.FOLDER_DIALOG, directory=str(self._root() or ""))
        if result:
            return str(result[0])
        return None

    def pick_font(self):
        if WINDOW is None:
            return None
        result = WINDOW.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("Font files (*.ttf;*.otf)", "All files (*.*)"),
        )
        if result:
            return str(result[0])
        return None

    def install_mod(self):
        try:
            paks = self._paks()
            if not paks.exists():
                return {"ok": False, "msg": "Không tìm thấy thư mục Paks của game."}
            dst = paks / "~mods" / "Dungeons-Vietnamese"
            # Phòng trường hợp đường dẫn này từng bị tạo nhầm thành một file
            if dst.exists() and not dst.is_dir():
                dst.unlink()
            dst.mkdir(parents=True, exist_ok=True)
            for name in ("Dungeons-Vietnamese_P.pak", "Dungeons-Vietnamese_P.ucas",
                         "Dungeons-Vietnamese_P.utoc"):
                src = ASSETS / "mod_files" / name
                if not src.exists():
                    return {"ok": False, "msg": f"Thiếu file mod: {name}"}
                shutil.copy2(src, dst / name)
            return {"ok": True, "msg": "Đã cài tiếng Việt. Mở game → Cài đặt → Ngôn ngữ văn bản → Tiếng Việt."}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def uninstall_mod(self):
        mods = self._paks() / "~mods"
        dst = mods / "Dungeons-Vietnamese"
        removed = False
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst, ignore_errors=True)
            else:
                dst.unlink()
            removed = True
        # Gỡ luôn font tuỳ chỉnh để game về lại font Minecraft gốc
        fonts = 0
        if mods.exists():
            for d in mods.iterdir():
                if d.is_dir() and d.name.endswith("_99"):
                    shutil.rmtree(d, ignore_errors=True)
                    fonts += 1
        CFG["font_name"] = ""
        save_cfg(CFG)
        if removed:
            return {"ok": True, "msg": f"Đã gỡ mod tiếng Việt và {fonts} gói font tuỳ chỉnh. Game dùng lại font Minecraft gốc."}
        return {"ok": False, "msg": "Chưa cài mod tiếng Việt."}

    def open_game_folder(self):
        root = self._root()
        if root.exists():
            subprocess.Popen(["explorer.exe", str(root)], creationflags=NO_WINDOW)
            return {"ok": True, "msg": "Đã mở thư mục game."}
        return {"ok": False, "msg": "Không tìm thấy thư mục game."}

    def play(self):
        exe = self._root() / "Dungeons.exe"
        if not exe.exists():
            return {"ok": False, "msg": "Không tìm thấy Dungeons.exe."}
        subprocess.Popen([str(exe)], cwd=str(exe.parent), creationflags=NO_WINDOW)
        return {"ok": True, "msg": "Đã khởi động game. Lần đầu có thể mất 2-3 phút để nạp shader."}

    def install_font(self, font_path, name):
        try:
            paks = self._paks()
            if not paks.exists():
                return {"ok": False, "msg": "Không tìm thấy thư mục Paks."}
            f = Path(font_path or "")
            if not f.is_file():
                return {"ok": False, "msg": "Chọn file TTF/OTF trước."}
            data = f.read_bytes()
            tag = data[0:4]
            if tag not in (b"OTTO", b"\x00\x01\x00\x00", b"true", b"ttcf") and data[4:8] not in (b"OTTO", b"\x00\x01\x00\x00"):
                return {"ok": False, "msg": "File không phải TTF/OTF hợp lệ."}
            name = (name or f.stem).strip().replace(" ", "_")
            padded = data + b"\x00" * ((-len(data)) % 4)
            ufont = struct.pack("<I", len(padded)) + padded + b"\x00" * 4

            work = Path(os.environ.get("TEMP", "")) / "mcd2_font_build"
            if work.exists():
                shutil.rmtree(work, ignore_errors=True)
            for rel in load_font_assets():
                out = work / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(ufont)

            repak = ASSETS / "tools" / "repak.exe"
            retoc = ASSETS / "tools" / "retoc.exe"
            if not repak.exists() or not retoc.exists():
                return {"ok": False, "msg": "Thiếu công cụ đóng gói trong exe."}

            subprocess.run([str(repak), "pack", str(work), "-q", str(work.with_suffix(".pak"))],
                           check=True, capture_output=True, creationflags=NO_WINDOW)
            packed = work.with_suffix(".pak")
            mod_dir = paks / "~mods" / f"{name}_99"
            mod_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(packed, mod_dir / f"{name}_99_P.pak")
            subprocess.run([str(retoc), "to-zen", "--version", "UE5_6",
                            f"{name}_99_P.pak", f"{name}_99_P.utoc"],
                           cwd=str(mod_dir), check=True, capture_output=True, creationflags=NO_WINDOW)
            packed.unlink(missing_ok=True)
            shutil.rmtree(work, ignore_errors=True)
            CFG["font_name"] = name
            save_cfg(CFG)
            return {"ok": True, "msg": f"Đã cài font '{name}'. Khởi động lại game để áp dụng."}
        except Exception as e:
            return {"ok": False, "msg": f"Lỗi: {e}"}

    # ---------------- graphics ----------------
    def _graphics_ini(self):
        return (Path(os.environ.get("LOCALAPPDATA", "")) / "Dungeons2" / "Saved"
                / "Config" / "WinGDK" / "GameUserSettings.ini")

    def game_running(self):
        try:
            r = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Dungeons-WinGDK-Shipping.exe"],
                capture_output=True, text=True, timeout=10, creationflags=NO_WINDOW,
            )
            return "Dungeons-WinGDK-Shipping.exe" in r.stdout
        except Exception:
            return False

    def get_graphics(self):
        path = self._graphics_ini()
        if not path.exists():
            return {"ok": False, "msg": "Chưa tìm thấy GameUserSettings.ini. Hãy mở game ít nhất một lần."}
        text = path.read_text(encoding="utf-8", errors="ignore")
        vals = {}
        section = ""
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                section = s[1:-1]
                continue
            if "=" in s and not s.startswith(";"):
                k, v = s.split("=", 1)
                if section in ("ScalabilityGroups", "/Script/Engine.GameUserSettings"):
                    vals[k.strip()] = v.strip()
        return {"ok": True, "values": vals, "running": self.game_running()}

    def _set_ini_section(self, path, section, mapping):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        out = []
        current = ""
        seen = set()
        for line in lines:
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                current = s[1:-1]
                out.append(line)
                continue
            key = s.split("=", 1)[0].strip() if "=" in s and not s.startswith(";") else None
            if current == section and key in mapping and key not in seen:
                out.append(f"{key}={mapping[key]}")
                seen.add(key)
            else:
                out.append(line)
        for k, v in mapping.items():
            if k not in seen:
                out.append(f"{k}={v}")
        path.write_text("\n".join(out) + "\n", encoding="utf-8")

    def set_graphics(self, values):
        path = self._graphics_ini()
        if not path.exists():
            return {"ok": False, "msg": "Chưa tìm thấy GameUserSettings.ini."}
        sg_keys = [
            "sg.ResolutionQuality", "sg.ViewDistanceQuality", "sg.AntiAliasingQuality",
            "sg.ShadowQuality", "sg.GlobalIlluminationQuality", "sg.ReflectionQuality",
            "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality",
            "sg.FoliageQuality", "sg.ShadingQuality", "sg.LandscapeQuality",
        ]
        sg = {k: str(values.get(k, "")) for k in sg_keys if values.get(k, "") != ""}
        sys_keys = ["ResolutionSizeX", "ResolutionSizeY", "FullscreenMode", "bUseVSync", "FrameRateLimit"]
        sysv = {k: str(values[k]) for k in sys_keys if k in values}
        if sg:
            self._set_ini_section(path, "ScalabilityGroups", sg)
        if sysv:
            self._set_ini_section(path, "/Script/Engine.GameUserSettings", sysv)
        running = self.game_running()
        msg = "Đã lưu cấu hình đồ hoạ."
        if running:
            msg += " ⚠ Game đang chạy: vui lòng THOÁT game rồi vào lại để áp dụng."
        return {"ok": True, "msg": msg, "running": running}

    def restore_font(self):
        paks = self._paks()
        n = 0
        if (paks / "~mods").exists():
            for d in (paks / "~mods").iterdir():
                if d.is_dir() and d.name.endswith("_99"):
                    shutil.rmtree(d, ignore_errors=True)
                    n += 1
        CFG["font_name"] = ""
        save_cfg(CFG)
        return {"ok": True, "msg": f"Đã gỡ {n} gói font tuỳ chỉnh, dùng lại font JBM mặc định của bản Việt hoá."}


def webview2_installed():
    guid = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients"),
    ]
    for root, path in locations:
        try:
            with winreg.OpenKey(root, path + "\\" + guid):
                return True
        except OSError:
            pass
    return False


def ensure_webview2():
    if webview2_installed():
        return
    installer = ASSETS / "WebView2RuntimeInstallerX64.exe"
    if not installer.exists():
        return
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Launcher cần WebView2 Runtime. Đang cài đặt tự động (chỉ lần đầu), vui lòng đợi trong vài phút...",
            "MCD2 VH Launcher",
            0x40,
        )
    except Exception:
        pass
    tmp = Path(os.environ.get("TEMP", "")) / installer.name
    try:
        shutil.copy2(installer, tmp)
        subprocess.run([str(tmp), "/silent", "/install"], timeout=900, creationflags=NO_WINDOW)
    except Exception:
        pass
    finally:
        tmp.unlink(missing_ok=True)


def main():
    global WINDOW
    ensure_webview2()
    api = Api()
    WINDOW = webview.create_window(
        "Minecraft Dungeons II - VH Launcher",
        str(BASE / "ui.html"),
        js_api=api,
        width=1280,
        height=760,
        maximized=True,
        min_size=(1100, 680),
        background_color="#0b1020",
        text_select=False,
    )
    def maximize_later():
        time.sleep(3)
        try:
            WINDOW.maximize()
        except Exception:
            pass

    threading.Thread(target=maximize_later, daemon=True).start()
    webview.start()


if __name__ == "__main__":
    main()
