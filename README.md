[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-checked-blue)](https://www.virustotal.com/gui/file/35f576b23fb2d53199602a65115165527130665abf5bb8a95331e410098a103b?nocache=1)

# Minecraft Dungeons II — Bản Việt hoá cộng đồng

Bản dịch tiếng Việt cho **Minecraft Dungeons II (PC, bản 1.1.3.0)**, kèm launcher WebView đóng gói thành một file exe duy nhất.

> Made by **HuyNhatTran** via Discord <3

## Tải về & cài đặt nhanh

Repo này **không chứa sẵn file mod hay file exe** (xem [Các file không nằm trong repo](#các-file-không-nằm-trong-repo)). **Tải tại đây → [Release](https://github.com/HuyNhatTraan/minecraft-dungeon-ii-viet-hoa/releases)**.

### Ảnh chụp giao diện

| Trang chủ | Font tuỳ chỉnh |
| :---: | :---: |
| ![Trang chủ launcher](screenshots/Screenshot%202026-11-24%20202605.png) | ![Tab Font tuỳ chỉnh](screenshots/Screenshot%202026-11-24%20202623.png) |

| Đồ hoạ | Thông tin |
| :---: | :---: |
| ![Tab Đồ hoạ](screenshots/Screenshot%202026-11-24%20202629.png) | ![Tab Thông tin](screenshots/Screenshot%202026-11-24%20202635.png) |

## Launcher

- Chọn đường dẫn game, Cài / Gỡ Việt hoá, Chơi game.
- **Font tuỳ chỉnh**: chọn TTF/OTF → ghi đè 21 font Latin/pixel, đóng gói thành `~mods\<Tên>_99\`. Nút "Dùng font JBM mặc định" để quay lại.
- **Đồ hoạ**: độ phân giải, fullscreen, VSync, FPS limit, tỷ lệ render, 6 nhóm chất lượng. Nhắc thoát game nếu phát hiện game đang chạy.
- Nền video, credit và QR ủng hộ trong tab **Thông tin** (QR mặc định bị che, bấm để xem).

## Build từ source

```bat
pip install pywebview pyinstaller pillow
launcher\build.bat
```

`build.py` tự tải WebView2 Runtime standalone (x64) từ link chính thức của Microsoft, kiểm tra SHA-256, rồi đóng gói thành `launcher\dist\MCD2_VH_Launcher.exe` (~300 MB). WebView2 installer (~203 MB) và file exe **không được commit**.

> ⚠️ Chạy `python launcher.py` trực tiếp từ source sẽ **thiếu một số tính năng** vì các asset sau nằm ngoài repo: `assets/mod_files/` (nút Cài Việt hoá báo "Thiếu file mod"), `assets/tools/repak.exe` + `retoc.exe` (font tuỳ chỉnh), `font.ttf` / `font-bold.ttf` (UI dùng font hệ thống), `bg.mp4` và `donate.png` (mất video nền / QR). Dùng exe bản phát hành để có đầy đủ tính năng.

## Cấu trúc repo

```
MCD2-Vietnamese/
├── launcher/
│   ├── launcher.py        # backend pywebview: cài mod, font, đồ hoạ...
│   ├── ui.html            # toàn bộ giao diện (HTML/CSS/JS)
│   ├── build.py           # script build exe một file (tự tải WebView2)
│   ├── build.bat          # wrapper chạy build.py
│   └── assets/            # chỉ logo.jpg / logo.ico / donate.png được commit
├── screenshots/           # ảnh chụp giao diện
├── .gitignore
├── LICENSE
└── README.md
```

## Các file không nằm trong repo

| Đường dẫn | Lý do |
|---|---|
| `mod/`, `*.pak`, `*.ucas`, `*.utoc` | File mod / pak đã đóng gói — phát hành qua Releases, không commit. |
| `launcher/assets/mod_files/` | Bản copy của mod để nhúng vào exe. |
| `launcher/assets/font*.ttf`, `bg.mp4`, `font_paths.txt` | Font và video (~50 MB); một số liên quan đến asset của game. |
| `launcher/assets/tools/*.exe`, `oo2core_9_win64.dll` | Công cụ đóng gói bên thứ ba (~10 MB). |
| `launcher/assets/WebView2RuntimeInstallerX64.exe` | ~203 MB, được `build.py` tải lại khi build. |
| `launcher/dist/`, `launcher/build/`, `*.spec` | Kết quả build PyInstaller. |
| `localization/` (gồm `extracted/`) | Toàn bộ quy trình dịch và locres gốc — **không công khai** trong repo này (cả AES key dùng để giải pak game). |

## Giấy phép & lưu ý

- Mã nguồn launcher trong repo này được cấp theo [MIT](LICENSE) — tự do dùng / sửa / phân phối, giữ credit **HuyNhatTran**. Bản dịch và file mod phát hành riêng qua tab **Releases**: dùng được tự do, nhưng source quy trình dịch không công khai.
- **Không** đính kèm file game, locres gốc hay asset bản quyền của Mojang/Microsoft. Dữ liệu dịch được trích và xử lý từ bản game người dùng tự sở hữu; quy trình đó không nằm trong repo này.
- Bản dịch trích từ game **1.1.3.0**; bản khác có thể lệch key → một số chỗ hiện tiếng Anh.
- Game GDK/OnlineFix và lỗi khởi động của bản game không liên quan đến mod này.

## Credit

Made by **HuyNhatTran** via Discord <3

Nếu thấy bản Việt hoá hữu ích, bạn có thể ủng hộ qua QR trong tab **Thông tin** của launcher.
