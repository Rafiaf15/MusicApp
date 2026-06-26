import subprocess
import sys
import os
import time
from PyQt5.QtCore import QThread, pyqtSignal

# Fix translation issue untuk PyInstaller
if getattr(sys, 'frozen', False):
    os.environ['LANG'] = 'en_US'
    os.environ['LANGUAGE'] = 'en_US'

from ytmusicapi import YTMusic

# ✅ Custom headers untuk menghindari blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ✅ Inisialisasi ytmusic dengan retry
ytmusic = None

def init_ytmusic():
    """Inisialisasi ytmusic dengan retry mechanism"""
    global ytmusic
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Initializing ytmusic (attempt {attempt + 1}/{max_retries})...")
            ytmusic = YTMusic(headers=HEADERS)
            # Test koneksi
            ytmusic.search("test", limit=1)
            print("✅ ytmusicapi initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    # Fallback: coba tanpa headers
    try:
        print("🔄 Trying without headers...")
        ytmusic = YTMusic()
        print("✅ ytmusicapi initialized without headers")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize ytmusic: {e}")
        return False

# Inisialisasi saat module load
init_ytmusic()

# ✅ Flag untuk Windows agar tidak memunculkan CMD window
CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0


class SearchThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            print(f"🔍 Searching for: {self.query}")
            
            # Pastikan ytmusic terinisialisasi
            if ytmusic is None:
                if not init_ytmusic():
                    # Fallback ke yt-dlp search
                    print("⚠️ ytmusic failed, trying yt-dlp search...")
                    self.search_with_ytdlp()
                    return
            
            # Coba search dengan retry
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # 1) Coba filter lagu dulu
                    results = ytmusic.search(self.query, filter='songs', limit=10)
                    print(f"✅ Found {len(results)} results with 'songs' filter")

                    # 2) Fallback kalau kosong
                    if not results:
                        print("⚠️ No results with 'songs' filter, trying 'videos'...")
                        results = ytmusic.search(self.query, filter='videos', limit=10)
                        print(f"✅ Found {len(results)} results with 'videos' filter")

                    # 3) Fallback terakhir tanpa filter
                    if not results:
                        print("⚠️ No results with filter, trying without filter...")
                        results = ytmusic.search(self.query, limit=10)
                        print(f"✅ Found {len(results)} results without filter")

                    self.finished.emit((results or [])[:10])
                    return
                    
                except Exception as search_error:
                    print(f"⚠️ Search attempt {attempt + 1} failed: {search_error}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        # Semua retry gagal, fallback ke yt-dlp
                        print("⚠️ All ytmusic retries failed, trying yt-dlp...")
                        self.search_with_ytdlp()
                        return
                        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.search_with_ytdlp()

    def search_with_ytdlp(self):
        """Fallback search menggunakan yt-dlp"""
        try:
            print(f"🔍 Searching with yt-dlp for: {self.query}")
            
            cmd = [
                'yt-dlp',
                '--default-search', 'ytsearch',
                '--no-playlist',
                '--flat-playlist',
                f'ytsearch10:{self.query}',
                '--print', '%(id)s|||%(title)s|||%(uploader)s|||%(duration)s'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=CREATION_FLAGS
            )
            
            if result.returncode == 0 and result.stdout.strip():
                results = []
                for line in result.stdout.strip().split('\n'):
                    if line and '|||' in line:
                        parts = line.split('|||')
                        if len(parts) >= 3:
                            results.append({
                                'videoId': parts[0],
                                'title': parts[1],
                                'artists': [{'name': parts[2]}],
                                'duration': parts[3] if len(parts) > 3 else ''
                            })
                
                if results:
                    print(f"✅ Found {len(results)} results via yt-dlp")
                    self.finished.emit(results)
                else:
                    self.error.emit("Tidak ada hasil ditemukan (yt-dlp)")
            else:
                self.error.emit(f"yt-dlp search failed: {result.stderr}")
                
        except Exception as e:
            self.error.emit(f"Fallback search error: {str(e)}")


class URLFetchThread(QThread):
    """Fetch URL untuk semua lagu sekaligus di background"""
    url_ready = pyqtSignal(int, str)
    fetch_complete = pyqtSignal()
    error = pyqtSignal(int, str)

    def __init__(self, songs_with_indices):
        super().__init__()
        self.songs_with_indices = songs_with_indices

    def run(self):
        for index, song in self.songs_with_indices:
            video_id = song.get("videoId")
            if not video_id:
                self.error.emit(index, "No video ID")
                continue
            
            try:
                cmd = [
                    'yt-dlp',
                    '-f', 'bestaudio[ext=m4a]/bestaudio',
                    '--get-url',
                    '--no-warnings',
                    '--socket-timeout', '10',
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=20,
                    creationflags=CREATION_FLAGS
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    url = result.stdout.strip()
                    self.url_ready.emit(index, url)
                else:
                    self.error.emit(index, "Failed to get URL")
            except Exception as e:
                self.error.emit(index, str(e))
        
        self.fetch_complete.emit()