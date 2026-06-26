# 🎵 Music Player Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green?logo=qt)
![VLC](https://img.shields.io/badge/VLC-3.0+-orange?logo=vlc)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey)

**Aplikasi Music Player Desktop Modern dengan UI ala Spotify** 🎧✨

[Fitur](#-fitur) • [Instalasi](#-instalasi) • [Cara Pakai](#-cara-pakai) • [Kontribusi](#-kontribusi)

</div>

---

## 📖 Tentang

**Music Player Pro** adalah aplikasi pemutar musik desktop open-source yang dibangun dengan Python dan PyQt5. Aplikasi ini mengambil audio dari YouTube Music dan memputarnya dengan tampilan modern mirip Spotify, lengkap dengan fitur shuffle, repeat, system tray, dan keyboard shortcuts.

> ⚠️ **Catatan:** Aplikasi ini dibuat untuk tujuan edukasi. Pastikan Anda mematuhi ketentuan layanan YouTube saat menggunakannya.

---

## ✨ Fitur

### 🎨 Tampilan Modern
- 🌙 Dark theme ala Spotify
- 🖼️ Album art otomatis dari thumbnail
- 🎭 Icon FontAwesome yang smooth
- 📊 Progress bar dengan gradient
- 💫 Animasi dan efek hover

### 🎮 Kontrol Lengkap
- ⏯️ Play / Pause / Next / Previous
- 🔀 **Shuffle** - Putar lagu secara acak
- 🔁 **Repeat** - 3 mode (Off / All / One)
- 🔊 Volume control dengan slider
- ⏩ Seek ke posisi tertentu

### ⌨️ Keyboard Shortcuts
| Shortcut | Fungsi |
|----------|--------|
| `Space` | Play / Pause |
| `←` | Previous song |
| `→` | Next song |
| `↑` | Volume Up (+5%) |
| `↓` | Volume Down (-5%) |
| `M` | Mute / Unmute |
| `S` | Toggle Shuffle |
| `R` | Toggle Repeat |
| `Enter` | Search (di search box) |

### 📍 System Tray
- Minimize ke system tray saat close
- Kontrol playback dari tray icon
- Notifikasi desktop saat lagu siap
- Menu context di tray

### 🚀 Performa
- ⚡ Pre-fetch URL di background
- 💾 Cache URL untuk instant play
- 🧵 Multi-threading (tidak freeze)
- 🔄 Auto-play next song

---

## 📸 Screenshot

<div align="center">
  <img src="screenshots/main.png" alt="Main Window" width="800"/>
  <p><em>Tampilan utama Music Player Pro</em></p>
</div>

> 💡 Tambahkan screenshot Anda di folder `screenshots/`

---

## 📋 Requirements

### System Requirements
- Python 3.8 atau lebih baru
- VLC Media Player (wajib)
- yt-dlp (wajib)
- Koneksi internet

### Python Dependencies
```txt
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0
ytmusicapi>=1.5.0
yt-dlp>=2024.1.1
python-vlc>=3.0.18122
qtawesome>=1.3.0
requests>=2.31.0