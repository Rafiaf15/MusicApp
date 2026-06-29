import subprocess
import sys
from PyQt5.QtCore import QThread, pyqtSignal
import threading
from queue import Queue
import time

CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0


class URLFetchService(QThread):
    """Super fast URL fetcher dengan priority queue"""
    url_ready = pyqtSignal(int, str)
    fetch_complete = pyqtSignal()
    error = pyqtSignal(int, str)
    progress = pyqtSignal(int, int)
    
    def __init__(self, songs, max_workers=5):
        super().__init__()
        self.songs = songs
        self.max_workers = max_workers
        self._cancelled = False
        self._queue = Queue()
        self._results = {}
    
    def run(self):
        """Fetch URLs dengan multiple threads secara paralel"""
        total = len(self.songs)
        
        # Enqueue semua tasks
        for index, song in enumerate(self.songs):
            self._queue.put((index, song))
        
        # Worker threads
        workers = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            workers.append(t)
        
        # Wait semua workers
        for t in workers:
            t.join()
        
        if not self._cancelled:
            self.fetch_complete.emit()
    
    def _worker(self):
        """Worker thread untuk fetch URLs"""
        while not self._cancelled and not self._queue.empty():
            try:
                index, song = self._queue.get_nowait()
                url = self._fetch_url_fast(index, song)
                if url:
                    self._results[index] = url
                    self.url_ready.emit(index, url)
                self._queue.task_done()
            except:
                break
    
    def _fetch_url_fast(self, index, song):
        """Fetch URL dengan opsi yang lebih cepat"""
        video_id = song.get("videoId")
        if not video_id:
            return None
        
        try:
            # Opsi yang LEBIH CEPAT
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio',
                '--get-url',
                '--no-warnings',
                '--no-playlist',
                '--socket-timeout', '5',  # Lebih cepat timeout
                '--extractor-retries', '1',  # Hanya 1x retry
                '--http-chunk-size', '1048576',  # 1MB chunks
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # Timeout lebih singkat
                creationflags=CREATION_FLAGS
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
            
        except Exception:
            return None
    
    def get_priority_url(self, index):
        """Get URL dengan prioritas tinggi (untuk lagu yang sedang diklik)"""
        if index in self._results:
            return self._results[index]
        return None
    
    def cancel(self):
        self._cancelled = True