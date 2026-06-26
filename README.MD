# 🎵 Music Player Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python\&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green?logo=qt)
![VLC](https://img.shields.io/badge/VLC-3.0+-orange?logo=vlc)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey)

**Aplikasi Music Player Desktop Modern dengan UI ala Spotify** 🎧✨

[Fitur](#-fitur) • [Instalasi](#-instalasi) • [Cara Pakai](#-cara-pakai) • [Kontribusi](#-kontribusi)

</div>

---

## 📖 Tentang

**Music Player Pro** adalah aplikasi pemutar musik desktop berbasis Python dan PyQt5 dengan tampilan modern menyerupai Spotify. Aplikasi ini mengambil audio dari YouTube Music dan memutarnya menggunakan VLC sebagai backend.

> ⚠️ **Catatan:** Project ini dibuat untuk tujuan edukasi. Pastikan penggunaan tetap sesuai dengan kebijakan YouTube.

---

## ✨ Fitur

### 🎨 UI & Experience

* Dark theme modern ala Spotify
* Album art otomatis dari thumbnail
* Icon menggunakan FontAwesome
* Progress bar dengan efek gradient
* Animasi dan efek hover

### 🎮 Kontrol Playback

* Play / Pause / Next / Previous
* Shuffle mode (acak lagu)
* Repeat mode (Off / All / One)
* Volume control
* Seek lagu (loncat ke durasi tertentu)

### ⌨️ Keyboard Shortcuts

| Shortcut | Fungsi          |
| -------- | --------------- |
| Space    | Play / Pause    |
| ←        | Lagu sebelumnya |
| →        | Lagu berikutnya |
| ↑        | Volume naik     |
| ↓        | Volume turun    |
| M        | Mute / Unmute   |
| S        | Toggle Shuffle  |
| R        | Toggle Repeat   |
| Enter    | Search          |

### 📍 System Tray

* Minimize ke tray saat close
* Kontrol playback dari tray
* Notifikasi desktop
* Context menu

### 🚀 Performa

* Pre-fetch URL di background
* Cache untuk playback cepat
* Multi-threading (tidak freeze)
* Auto-play next song

---

## 📋 Requirements

### System

* Python 3.8+
* VLC Media Player
* yt-dlp
* Koneksi internet

### Python Dependencies

```txt
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0
ytmusicapi>=1.5.0
yt-dlp>=2024.1.1
python-vlc>=3.0.18122
qtawesome>=1.3.0
requests>=2.31.0
```

---

## 🚀 Instalasi

### 1. Install VLC

Download dari: https://www.videolan.org/

### 2. Install yt-dlp

```bash
pip install yt-dlp
```

### 3. Clone Repository

```bash
git clone https://github.com/username/music-player-pro.git
cd music-player-pro
```

### 4. Virtual Environment (Opsional)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Cara Menjalankan

### Run dari Source

```bash
python main.py
```

### Build ke Executable (Windows)

```bash
pyinstaller --onefile --noconsole main.py
```

Output ada di:

```
dist/MusicPlayerPro.exe
```

---

## 📁 Struktur Project

```
music-player-pro/
│
├── assets/
├── core/
├── ui/
├── utils/
├── threads/
├── screenshots/
├── main.py
└── requirements.txt
```

---

## 🛠️ Troubleshooting

**Error: python-vlc tidak ditemukan**
→ Pastikan VLC sudah terinstall

**Error: yt-dlp tidak ditemukan**
→ Install dengan `pip install yt-dlp`

**CMD muncul saat play**
→ Gunakan flag `CREATE_NO_WINDOW` pada subprocess

**Lagu tidak bisa diputar**
→ Pastikan VLC terinstall dengan benar

**Search tidak muncul hasil**
→

* Cek koneksi internet
* Update ytmusicapi
* Gunakan keyword umum

**SSL Error**

```bash
pip install --upgrade certifi
```

---

## 🤝 Kontribusi

Kontribusi sangat terbuka.

### Alur Kontribusi

1. Fork repository
2. Buat branch baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

### Format Commit

* feat: fitur baru
* fix: perbaikan bug
* docs: dokumentasi
* refactor: perbaikan struktur kode

---

## 🎯 Roadmap Pengembangan

* Equalizer audio
* Download lagu offline
* Playlist management
* Lyrics display
* Audio visualizer
* Multi-language
* Crossfade antar lagu
* Export playlist
* Mobile version

---

## 📄 License

Project ini menggunakan **MIT License**.

---

## 🙏 Credits

* YouTube Music
* VLC Media Player
* PyQt5
* yt-dlp
* ytmusicapi
* QtAwesome

---

## 📞 Kontak

* Issues: GitHub Issues
* Discussions: GitHub Discussions

---

## ⭐ Star History

<a href="https://star-history.com/#Rafiaf15/music-player-pro&Date">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://api.star-history.com/svg?repos=Rafiaf15/music-player-pro&type=Date&theme=dark" />
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://api.star-history.com/svg?repos=Rafiaf15/music-player-pro&type=Date" />
    <img
      alt="Star History Chart"
      src="https://api.star-history.com/svg?repos=Rafiaf15/music-player-pro&type=Date" />
  </picture>
</a>